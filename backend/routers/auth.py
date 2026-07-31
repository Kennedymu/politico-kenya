from fastapi import APIRouter, HTTPException
import bcrypt

from backend.database import get_connection
from backend.schemas.user import UserRegistration, UserLogin

router = APIRouter(tags=["Authentication"])


@router.post("/register")
def register(user: UserRegistration):

    conn = get_connection()
    cursor = conn.cursor()

    # Check National ID
    cursor.execute(
        "SELECT id FROM users WHERE national_id = ?",
        (user.national_id,)
    )

    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="National ID already registered."
        )

    # Check Email
    cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        (user.email,)
    )

    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    password_hash = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # Save User
    cursor.execute("""
        INSERT INTO users
        (national_id, full_name, email, phone, password_hash, role)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user.national_id,
        user.full_name,
        user.email,
        user.phone,
        password_hash,
        "voter"
    ))

    user_id = cursor.lastrowid

    # Save Voter
    cursor.execute("""
        INSERT INTO voters
        (user_id, county_id, constituency_id, ward_id, polling_station)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        user.county_id,
        user.constituency_id,
        user.ward_id,
        user.polling_station
    ))

    conn.commit()
    conn.close()

    return {
        "message": "Registration successful",
        "user_id": user_id
    }

@router.post("/login")
def login(user: UserLogin):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, national_id, full_name, password_hash, role
        FROM users
        WHERE national_id = ?
    """, (user.national_id,))

    db_user = cursor.fetchone()

    if not db_user:
        conn.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid National ID or password."
        )

    password_ok = bcrypt.checkpw(
        user.password.encode("utf-8"),
        db_user["password_hash"].encode("utf-8")
    )

    if not password_ok:
        conn.close()
        raise HTTPException(
            status_code=401,
            detail="Invalid National ID or password."
        )

    conn.close()

    return {
        "message": "Login successful",
        "user_id": db_user["id"],
        "full_name": db_user["full_name"],
        "role": db_user["role"]
    }