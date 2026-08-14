from typing import Optional
import database


def hash_password(password: str) -> str:
    # database._hash_text is internal but reuse for consistency
    try:
        return database._hash_text(password)
    except Exception:
        # fallback
        import hashlib

        return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def login(username: str, password: str) -> Optional[dict]:
    user = database.get_user_by_username(username)
    if not user:
        return None
    if verify_password(password, user.get("password_hash", "")):
        # return safe user dict
        return {"id": user["id"], "username": user["username"], "role": user["role"]}
    return None


def register_user(username: str, password: str, role: str) -> int:
    return database.create_user(username, password, role)