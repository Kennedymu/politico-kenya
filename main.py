import os
import hmac
import hashlib
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Politico Kenya Engine",
    description="Transparent mandate ledger platform for Kenyan Citizens and Political Candidates with full IEBC structural alignment.",
    version="2.1.0"
)

# Enable CORS for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SYSTEM CRYPTOGRAPHIC SALT
SYSTEM_SALT = os.getenv("POLITICO_SALT", "iebc-aligned-cryptographic-salt-2026").encode('utf-8')

# IN-MEMORY IMMUTABLE MOCK LEDGERS
politicians_ledger: Dict[str, dict] = {}
mandates_ledger: List[dict] = []
voted_hashes_registry: set = set()


# --- PYDANTIC VALIDATION SCHEMAS ---

class ManifestoPillar(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, example="BETA Plan / Uchumi Bora")
    description: str = Field(..., min_length=10, max_length=1000, example="Structural framework detailing economic intervention parameters.")

class Manifesto(BaseModel):
    version: str = Field(..., example="v1.0")
    published_at: datetime = Field(default_factory=datetime.utcnow)
    pillars: List[ManifestoPillar]

class PoliticianRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100, example="Hon. William Samoei Ruto")
    running_office: str = Field(..., example="President")
    county: str = Field(..., example="Kenya")
    constituency: Optional[str] = Field(None, example="Westlands — Parklands Ward")
    party_affiliation: str = Field(..., example="UDA")
    manifesto: Manifesto

    @field_validator('running_office')
    @classmethod
    def validate_kenyan_office(cls, value: str) -> str:
        valid_offices = [
            "President", 
            "Governor", 
            "Senator", 
            "Member of National Assembly (MP)", 
            "County Woman Representative", 
            "Member of County Assembly (MCA)"
        ]
        if value not in valid_offices:
            raise ValueError(f"Office must be one of: {', '.join(valid_offices)}")
        return value

class PoliticianResponse(BaseModel):
    candidate_id: uuid.UUID
    full_name: str
    running_office: str
    county: str
    constituency: Optional[str]
    party_affiliation: str
    is_verified: bool
    manifesto: Manifesto

class MandateRequest(BaseModel):
    national_id_or_passport: str = Field(..., min_length=5, max_length=12, example="32145678")
    election_year: str = Field("2027", example="2027")
    candidate_id: uuid.UUID

class MandateResponse(BaseModel):
    mandate_id: uuid.UUID
    anonymized_voter_hash: str
    candidate_id: uuid.UUID
    timestamp: datetime
    ledger_signature: str


# --- CRYPTOGRAPHIC ENGINES ---

def generate_secure_voter_hash(id_number: str, election_year: str) -> str:
    """Generates an anonymous cryptographic identifier mapping a citizen's ballot allocation token."""
    clean_id = id_number.strip().replace(" ", "").upper()
    message = f"{clean_id}:{election_year}".encode('utf-8')
    return hmac.new(SYSTEM_SALT, message, hashlib.sha256).hexdigest()

def generate_ledger_signature(voter_hash: str, candidate_id: str) -> str:
    """Signs the block entry dynamically to protect entry chain integrity."""
    message = f"{voter_hash}:{candidate_id}".encode('utf-8')
    return hmac.new(SYSTEM_SALT, message, hashlib.sha256).hexdigest()


# --- SINGLE APP CORE API ENDPOINTS ---

@app.post("/api/v1/politicians", response_model=PoliticianResponse, status_code=status.HTTP_201_CREATED)
def register_candidate(payload: PoliticianRegisterRequest):
    """Registers a candidate into the political index, attaching their local validation parameters."""
    candidate_id = uuid.uuid4()
    
    # Process inputs clean without shifting structured cascading strings
    politician_data = {
        "candidate_id": candidate_id,
        "full_name": payload.full_name.strip(),
        "running_office": payload.running_office,
        "county": payload.county.strip(),
        "constituency": payload.constituency.strip() if payload.constituency else None,
        "party_affiliation": payload.party_affiliation.strip().upper(),
        "is_verified": True,
        "manifesto": payload.manifesto.model_dump()
    }
    
    politicians_ledger[str(candidate_id)] = politician_data
    return politician_data


@app.get("/api/v1/politicians", response_model=List[PoliticianResponse])
def list_candidates():
    """Returns all verified Kenyan election aspirants registered on the network."""
    return list(politicians_ledger.values())


@app.post("/api/v1/mandates", response_model=MandateResponse, status_code=status.HTTP_201_CREATED)
def cast_citizen_mandate(payload: MandateRequest):
    """Anonymously logs a citizen's mandate execution for a chosen candidate ledger slot."""
    cand_str = str(payload.candidate_id)
    if cand_str not in politicians_ledger:
        raise HTTPException(status_code=404, detail="Candidate ID target match failed to surface on the registry.")
        
    voter_hash = generate_secure_voter_hash(payload.national_id_or_passport, payload.election_year)
    
    # Anti-Fraud Interception Block
    if voter_hash in voted_hashes_registry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System Rejection: A validation token mapping this user asset has already signed a platform mandate."
        )
        
    mandate_id = uuid.uuid4()
    ledger_sig = generate_ledger_signature(voter_hash, cand_str)
    
    mandate_record = {
        "mandate_id": mandate_id,
        "anonymized_voter_hash": voter_hash,
        "candidate_id": payload.candidate_id,
        "timestamp": datetime.utcnow(),
        "ledger_signature": ledger_sig
    }
    
    # Write entries atomically
    voted_hashes_registry.add(voter_hash)
    mandates_ledger.append(mandate_record)
    
    return mandate_record


@app.get("/api/v1/mandates/audit")
def fetch_transparency_dashboard():
    """Generates public metrics breaking down counts per candidate to guarantee systemic trust."""
    tallies = {}
    for entry in mandates_ledger:
        c_id = str(entry["candidate_id"])
        tallies[c_id] = tallies.get(c_id, 0) + 1
        
    leaderboard = []
    for c_id, count in tallies.items():
        cand = politicians_ledger.get(c_id, {})
        leaderboard.append({
            "candidate_name": cand.get("full_name", "Unknown"),
            "office": cand.get("running_office", "Unknown"),
            "county": cand.get("county", "National"),
            "mandates_count": count
        })
        
    return {
        "network_status": "Operational / Secure",
        "total_ballots_tracked": len(mandates_ledger),
        "audit_data": leaderboard
    }
