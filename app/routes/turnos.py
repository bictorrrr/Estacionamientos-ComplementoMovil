from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.web import templates
from app.database import get_db
from app.models import Mensaje, Turno, Usuario
from app.routes.user import _is_admin_user, get_current_user

router = APIRouter()


@router.get("/turnos/abiertos")
def turnos_abiertos_view(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not _is_admin_user(current_user):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=302)

    turnos = db.query(Turno).filter(Turno.estado == "activo").all()
    turnos_ids = [turno.id for turno in turnos]

    mensajes_por_turno = {}
    if turnos_ids:
        filas = (
            db.query(
                Mensaje.turno_id,
                func.count(Mensaje.id).label("total"),
                func.sum(
                    case(
                        (Mensaje.estado == "pendiente", 1),
                        else_=0,
                    )
                ).label("pendientes"),
            )
            .filter(Mensaje.turno_id.in_(turnos_ids))
            .group_by(Mensaje.turno_id)
            .all()
        )

        mensajes_por_turno = {
            fila.turno_id: {
                "total": int(fila.total or 0),
                "pendientes": int(fila.pendientes or 0),
            }
            for fila in filas
        }

    return templates.TemplateResponse(
        "turnos_activos.html",
        {
            "request": request,
            "turnos": turnos,
            "mensajes_por_turno": mensajes_por_turno,
            "active_view": "turnos-abiertos",
        },
    )


@router.get("/activos")
def turnos_activos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    turnos = db.query(Turno).filter(Turno.estado == "activo").all()

    if not turnos:
        raise HTTPException(status_code=404, detail="No hay turnos activos")

    return turnos
