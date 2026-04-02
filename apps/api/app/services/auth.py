from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.errors import ConflictError, NotFoundError, ValidationError
from app.models.tender import User

PBKDF2_ITERATIONS = 600_000


def create_user_account(
    db: Session,
    *,
    full_name: str,
    email: str,
    password: str,
    company_name: str | None,
) -> User:
    from app.services.company_profiles import ensure_user_company_profile

    normalized_email = email.strip().lower()
    validate_email(normalized_email)
    existing = db.execute(select(User).where(User.email == normalized_email)).scalar_one_or_none()
    if existing is not None:
        raise ConflictError(f"User already exists: {normalized_email}")

    validate_password(password)

    user = User(
        email=normalized_email,
        full_name=full_name.strip(),
        company_name=company_name.strip() if company_name and company_name.strip() else None,
        password_hash=hash_password(password),
        role="manager",
        is_active=True,
    )
    db.add(user)
    db.flush()
    ensure_user_company_profile(db, user)
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> User:
    normalized_email = email.strip().lower()
    validate_email(normalized_email)
    user = db.execute(select(User).where(User.email == normalized_email)).scalar_one_or_none()
    if user is None or not user.password_hash or not verify_password(password, user.password_hash):
        raise ValidationError("Email o contraseña inválidos")
    if not user.is_active:
        raise ValidationError("La cuenta está desactivada")
    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()


def require_user_by_id(db: Session, user_id: int) -> User:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise NotFoundError(f"User not found: {user_id}")
    return user


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt, expected_digest = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False

    computed_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations_raw),
    ).hex()
    return hmac.compare_digest(computed_digest, expected_digest)


def validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres")


def validate_email(email: str) -> None:
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValidationError("Ingresá un email válido")


def create_session_token(user: User) -> str:
    settings = get_settings()
    expires_at = int((datetime.now(tz=UTC) + timedelta(seconds=settings.session_max_age_seconds)).timestamp())
    payload = f"{user.id}:{expires_at}"
    signature = hmac.new(
        settings.session_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return urlsafe_b64encode(f"{payload}:{signature}".encode("utf-8")).decode("utf-8")


def read_session_user_id(token: str | None) -> int | None:
    if not token:
        return None

    settings = get_settings()
    try:
        decoded = urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        user_id_raw, expires_at_raw, signature = decoded.split(":", 2)
    except Exception:
        return None

    payload = f"{user_id_raw}:{expires_at_raw}"
    expected_signature = hmac.new(
        settings.session_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return None

    try:
        if int(expires_at_raw) < int(datetime.now(tz=UTC).timestamp()):
            return None
        return int(user_id_raw)
    except ValueError:
        return None
