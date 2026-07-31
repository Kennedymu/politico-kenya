from datetime import datetime, timedelta, UTC

from jose import jwt

# ------------------------------------------------------------------
# JWT Configuration
# ------------------------------------------------------------------

SECRET_KEY = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_IN_PRODUCTION"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    """
    Create a signed JWT access token.
    """

    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt