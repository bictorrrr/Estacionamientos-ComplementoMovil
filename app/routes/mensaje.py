from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.web import templates
from app.database import get_db
from app.models import Mensaje, Usuario
from app.routes.user import _is_admin_user, get_current_user

router = APIRouter()


def get_current_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if not _is_admin_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: solo administradores",
        )
    return current_user


@router.get("/mensajes/nuevo")
def enviar_mensaje_view(
    request: Request,
    turno_id: int = Query(...),
    admin: Usuario = Depends(get_current_admin),
):
    return templates.TemplateResponse(
        "enviar_mensaje.html",
        {"request": request, "turno_id": turno_id},
    )


class MensajeCreate(BaseModel):
    turno_id: int
    contenido: str


class MensajeEstadoUpdate(BaseModel):
    estado: str


@router.get("/mensajes/historial")
def historial_mensajes_view(
    request: Request,
    turno_id: int = Query(...),
    admin: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    mensajes = (
        db.query(Mensaje)
        .filter(Mensaje.turno_id == turno_id)
        .order_by(Mensaje.fecha_enviado.desc())
        .all()
    )

    pendientes = sum(1 for mensaje in mensajes if (mensaje.estado or "pendiente") == "pendiente")
    leidos = len(mensajes) - pendientes

    return templates.TemplateResponse(
        "historial_mensajes.html",
        {
            "request": request,
            "turno_id": turno_id,
            "mensajes": mensajes,
            "pendientes": pendientes,
            "leidos": leidos,
        },
    )


@router.post("/mensajes", status_code=status.HTTP_201_CREATED)
def crear_mensaje(
    datos: MensajeCreate,
    admin: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    nuevo_mensaje = Mensaje(
        turno_id=datos.turno_id,
        contenido=datos.contenido,
        admin_id=admin.id,
        estado="pendiente",
        fecha_enviado=datetime.now(),
    )

    db.add(nuevo_mensaje)
    db.commit()
    db.refresh(nuevo_mensaje)

    return nuevo_mensaje


@router.patch("/mensajes/{mensaje_id}/estado")
def actualizar_estado_mensaje(
    mensaje_id: int,
    datos: MensajeEstadoUpdate,
    admin: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    estado_normalizado = datos.estado.strip().lower()
    if estado_normalizado not in {"pendiente", "leido"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Usa 'pendiente' o 'leido'.",
        )

    mensaje = db.query(Mensaje).filter(Mensaje.id == mensaje_id).first()
    if not mensaje:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensaje no encontrado")

    mensaje.estado = estado_normalizado
    db.commit()

    return {
        "id": mensaje.id,
        "estado": mensaje.estado,
    }
