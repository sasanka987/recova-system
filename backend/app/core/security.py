from datetime import datetime, timedelta
from typing import Optional, Union, Any
import hashlib
import base64
import json
from app.core.config import settings


def get_password_hash(password: str) -> str:
    """Simple password hashing - we'll upgrade this later"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Simple password verification"""
    return get_password_hash(plain_password) == hashed_password


def create_access_token(
        subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Simple token creation - Fixed to use JSON format"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Use JSON format instead of colon-separated to avoid conflicts
    token_data = {
        "email": str(subject),
        "exp": expire.timestamp(),  # Use timestamp instead of ISO string
        "secret": settings.SECRET_KEY[:10]
    }

    # Convert to JSON then base64
    json_str = json.dumps(token_data)
    token_bytes = json_str.encode('utf-8')
    token = base64.b64encode(token_bytes).decode('utf-8')
    return token


def verify_token(token: str) -> Optional[str]:
    """Simple token verification - Fixed to use JSON format"""
    try:
        print(f"Verifying token: {token[:20]}...")

        # Decode base64 token
        token_bytes = base64.b64decode(token.encode('utf-8'))
        json_str = token_bytes.decode('utf-8')
        print(f"Decoded JSON: {json_str}")

        # Parse JSON
        token_data = json.loads(json_str)
        print(f"Parsed token data: {token_data}")

        # Extract fields
        email = token_data.get("email")
        exp_timestamp = token_data.get("exp")
        secret_part = token_data.get("secret")

        print(f"Extracted email: {email}")
        print(f"Expiry timestamp: {exp_timestamp}")
        print(f"Secret part: {secret_part}")

        # Check if token is expired
        if exp_timestamp and datetime.utcnow().timestamp() > exp_timestamp:
            print("Token expired")
            return None

        # Check secret part
        if secret_part != settings.SECRET_KEY[:10]:
            print(f"Secret mismatch: {secret_part} != {settings.SECRET_KEY[:10]}")
            return None

        print(f"Token verification successful for: {email}")
        return email

    except Exception as e:
        print(f"Token verification error: {e}")
        import traceback
        traceback.print_exc()
        return None