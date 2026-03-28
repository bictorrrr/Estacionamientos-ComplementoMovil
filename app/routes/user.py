import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario

router = APIRouter()


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value != 0

    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "si", "sí", "yes", "on"}

    return False


def _parse_roles(raw_roles: str | None) -> dict[str, bool]:
    if not raw_roles:
        return {}

    raw_text = raw_roles.strip()
    if not raw_text:
        return {}

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    roles: dict[str, bool] = {}
    for key, value in parsed.items():
        role_name = str(key).strip().lower()
        if not role_name:
            continue
        roles[role_name] = _to_bool(value)

    return roles


def _is_admin_user(user: Usuario) -> bool:
    roles = _parse_roles(user.rol)
    return bool(roles.get("admin", False))


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Usuario:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    return user


@router.get("/verify-admin")
def verify_admin_role(current_user: Usuario = Depends(get_current_user)):
    return {"admin": _is_admin_user(current_user)}
