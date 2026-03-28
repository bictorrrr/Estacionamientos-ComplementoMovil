from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.web import templates
from app.database import get_db
from app.models import Usuario
from app.core.security import verify_password
from app.routes.user import _is_admin_user

router = APIRouter()

@router.get("/login")
def login_view(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(
    request: Request,
    codigo: int = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Prevent stale sessions from keeping previous privileges during a new login attempt.
    request.session.clear()

    usuario = db.query(Usuario).filter(Usuario.codigo == codigo).first()

    if not usuario or not verify_password(password, usuario.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Credenciales incorrectas"}
        )

    if not _is_admin_user(usuario):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Acceso denegado: solo administradores"}
        )

    request.session["user_id"] = usuario.id

    return RedirectResponse(url="/dashboard", status_code=302)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)