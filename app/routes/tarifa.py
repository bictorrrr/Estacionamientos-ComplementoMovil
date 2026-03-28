from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.web import templates
from app.database import get_db
from app.models import Tarifa, Usuario
from app.routes.user import _is_admin_user, get_current_user

router = APIRouter()


@router.get("/tarifas/default")
def tarifa_default_view(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not _is_admin_user(current_user):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=302)

    tarifa = (
        db.query(Tarifa)
        .filter(Tarifa.default == 1, Tarifa.eliminado == 0)
        .order_by(Tarifa.id.desc())
        .first()
    )

    return templates.TemplateResponse(
        "tarifa_default.html",
        {
            "request": request,
            "tarifa": tarifa,
            "active_view": "tarifas-default",
        },
    )
