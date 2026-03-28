from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.web import templates
from app.database import get_db
from app.models import CurrentEstacionamiento, Usuario
from app.routes.user import _is_admin_user, get_current_user

router = APIRouter()

@router.get("/dashboard")
def dashboard(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not _is_admin_user(current_user):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=302)

    autos = db.query(CurrentEstacionamiento).all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "autos": autos,
            "active_view": "dashboard",
        }
    )