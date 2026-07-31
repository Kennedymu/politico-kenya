from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.database import get_connection

app = FastAPI(
    title="Politico API",
    description="Election Management System API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "status": "running",
        "message": "Welcome to the Politico API",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/counties")
def get_counties():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT county_id, county_name
        FROM counties
        ORDER BY county_name
    """)

    counties = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return counties


@app.get("/constituencies/{county_id}")
def get_constituencies(county_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT constituency_id, constituency_name
        FROM constituencies
        WHERE county_id = ?
        ORDER BY constituency_name
    """, (county_id,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No constituencies found.")

    return rows


@app.get("/wards/{constituency_id}")
def get_wards(constituency_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ward_id, ward_name
        FROM wards
        WHERE constituency_id = ?
        ORDER BY ward_name
    """, (constituency_id,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No wards found.")

    return rows