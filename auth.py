import base64
import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import database_models
from database_connection import session


TOKEN_EXPIRE_MINUTES = 60
PASSWORD_ITERATIONS = 100_000
ROLE_PERMISSIONS = {
    "admin": ("read", "write"),
    "editor": ("read", "write"),
    "viewer": ("read",),
}
ALLOWED_REGISTRATIONS = {
    "admin": {
        ("Alok", "aloksri2204@gmail.com"),
        ("Rohit", "rohit@gmail.com"),
    },
    "viewer": {
        ("Priya", "priya@example.com"),
    },
}
# Only users whose full name, email, and requested role match one of these pairs can register.
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthUser:
    id: int
    username: str
    email: str
    full_name: str
    role: str
    permissions: tuple[str, ...]


def _get_secret_key() -> str:
    """Return the signing secret used for bearer tokens."""
    return os.getenv("AUTH_SECRET_KEY", "dev-only-change-me")


def _normalize_full_name(full_name: str) -> str:
    """Normalize names so allowlist comparisons are case-insensitive."""
    return " ".join(full_name.strip().split()).casefold()


def _normalize_email(email: str) -> str:
    """Normalize emails before validation and storage."""
    return email.strip().casefold()


def _allowed_registration_pairs_for_role(role: str) -> set[tuple[str, str]]:
    """Return the normalized allowlist for a specific role."""
    return {
        (_normalize_full_name(full_name), _normalize_email(email))
        for full_name, email in ALLOWED_REGISTRATIONS.get(role, set())
    }


def _is_allowed_registration(full_name: str, email: str, role: str) -> bool:
    """Check whether a name and email are approved for the requested role."""
    return (
        _normalize_full_name(full_name),
        _normalize_email(email),
    ) in _allowed_registration_pairs_for_role(role)


def _urlsafe_b64encode(raw_bytes: bytes) -> str:
    """Encode bytes using URL-safe base64 without trailing padding."""
    return base64.urlsafe_b64encode(raw_bytes).rstrip(b"=").decode("utf-8")


def _urlsafe_b64decode(value: str) -> bytes:
    """Decode URL-safe base64 and restore stripped padding."""
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str, salt: str | None = None) -> str:
    """Create a salted password hash for secure storage."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    """Compare a plain password against a stored salted hash."""
    try:
        salt, stored_digest = password_hash.split("$", maxsplit=1)
    except ValueError:
        return False

    candidate_hash = hash_password(password, salt)
    return hmac.compare_digest(candidate_hash, f"{salt}${stored_digest}")


def create_access_token(user: database_models.User) -> str:
    """Build a signed bearer token for an authenticated user."""
    header = {"alg": "HS256", "typ": "JWT"}
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.username,
        "uid": user.id,
        "role": user.role,
        "exp": int(expires_at.timestamp()),
    }

    encoded_header = _urlsafe_b64encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    encoded_payload = _urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(
        _get_secret_key().encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    encoded_signature = _urlsafe_b64encode(signature)
    return f"{signing_input}.{encoded_signature}"


def decode_access_token(token: str) -> dict:
    """Validate and decode a signed bearer token payload."""
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
    except ValueError as exc:
        raise _unauthorized_exception("Invalid token format") from exc

    signing_input = f"{encoded_header}.{encoded_payload}"
    expected_signature = hmac.new(
        _get_secret_key().encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    if not hmac.compare_digest(
        _urlsafe_b64encode(expected_signature), encoded_signature
    ):
        raise _unauthorized_exception("Invalid token signature")

    try:
        payload = json.loads(_urlsafe_b64decode(encoded_payload).decode("utf-8"))
    except (json.JSONDecodeError, ValueError) as exc:
        raise _unauthorized_exception("Invalid token payload") from exc

    exp = payload.get("exp")
    if not isinstance(exp, int):
        raise _unauthorized_exception("Token expiry is missing")

    if datetime.now(timezone.utc).timestamp() > exp:
        raise _unauthorized_exception("Token has expired")

    return payload


def _unauthorized_exception(detail: str = "Could not validate credentials") -> HTTPException:
    """Return a standard 401 error for auth failures."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _forbidden_exception() -> HTTPException:
    """Return a standard 403 error for permission failures."""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to perform this action",
    )


def _serialize_user(user: database_models.User) -> AuthUser:
    """Convert a database user into the auth-friendly dataclass."""
    permissions = ROLE_PERMISSIONS.get(user.role, tuple())
    return AuthUser(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        permissions=tuple(permissions),
    )


def authenticate_user(db: Session, username: str, password: str) -> database_models.User | None:
    """Authenticate a user by username and password."""
    user = db.query(database_models.User).filter(
        database_models.User.username == username
    ).first()
    if not user or not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    full_name: str,
    role: str,
) -> database_models.User:
    """Create a new user after validating role and allowlist rules."""
    normalized_role = role.lower()
    if normalized_role not in ROLE_PERMISSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported role '{role}'. Use one of: {', '.join(ROLE_PERMISSIONS)}",
        )

    normalized_email = _normalize_email(email)
    normalized_full_name = " ".join(full_name.strip().split())
    if not _is_allowed_registration(
        normalized_full_name,
        normalized_email,
        normalized_role,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is allowed only for approved name, email, and role combinations",
        )

    existing_user = db.query(database_models.User).filter(
        database_models.User.username == username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{username}' already exists",
        )

    existing_email = db.query(database_models.User).filter(
        database_models.User.email == normalized_email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{normalized_email}' already exists",
        )

    user = database_models.User(
        username=username,
        email=normalized_email,
        password_hash=hash_password(password),
        full_name=normalized_full_name,
        role=normalized_role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthUser:
    """Resolve the current signed-in user from the bearer token."""
    if credentials is None:
        raise _unauthorized_exception("Authentication required")

    payload = decode_access_token(credentials.credentials)
    username = payload.get("sub")
    if not username:
        raise _unauthorized_exception("Token subject is missing")

    db = session()
    try:
        user = db.query(database_models.User).filter(
            database_models.User.username == username
        ).first()
        if not user or not user.is_active:
            raise _unauthorized_exception("User is inactive or missing")
        return _serialize_user(user)
    finally:
        db.close()


def require_read_access(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Allow only users with read permission."""
    if "read" not in current_user.permissions:
        raise _forbidden_exception()
    return current_user


def require_write_access(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Allow only users with write permission."""
    if "write" not in current_user.permissions:
        raise _forbidden_exception()
    return current_user
