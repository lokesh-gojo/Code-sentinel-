from typing import Optional
from fastapi import Header, HTTPException, status
import hmac
import hashlib
import json
import base64
from app.core.config import settings


def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """
    Validates Supabase JWT from the Authorization header.
    In development mode or when testing without Supabase credentials,
    falls back gracefully to 'local-dev-user' to enable 100% offline testing.
    """
    if not authorization:
        if settings.ENVIRONMENT == "development":
            return "local-dev-user"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]

    # Local development bypass token
    if token == "dev-token" or settings.ENVIRONMENT == "development" and settings.SUPABASE_JWT_SECRET == "mock-jwt-secret":
        return "local-dev-user"

    # Decode and verify Supabase JWT
    try:
        token_parts = token.split(".")
        if len(token_parts) != 3:
            raise ValueError("Malformed JWT token structure")

        payload_bytes = base64.urlsafe_b64decode(token_parts[1] + "==")
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Verify signature if production secret is configured
        if settings.SUPABASE_JWT_SECRET and settings.SUPABASE_JWT_SECRET != "mock-jwt-secret":
            signature = token_parts[2]
            signing_input = f"{token_parts[0]}.{token_parts[1]}".encode("utf-8")
            expected_sig = base64.urlsafe_b64encode(
                hmac.new(settings.SUPABASE_JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
            ).decode("utf-8").rstrip("=")
            if not hmac.compare_digest(signature, expected_sig):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token signature",
                )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing 'sub' subject claim",
            )
        return str(user_id)

    except HTTPException:
        raise
    except Exception as e:
        if settings.ENVIRONMENT == "development":
            return "local-dev-user"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
