from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.web import templates
from app.database import get_db
from app.models import CurrentEstacionamiento, Tarifa

router = APIRouter(tags=["public"])


def _normalizar_placa(placa: str) -> str:
    return placa.strip().upper()


def _minutos_transcurridos(fecha_entrada, hora_entrada) -> int:
    entrada = datetime.combine(fecha_entrada, hora_entrada)
    salida = datetime.now()
    minutos = int((salida - entrada).total_seconds() // 60)

    if minutos <= 0:
        raise ValueError("El tiempo transcurrido debe ser mayor a 0 minutos")

    return minutos


def _calcular_importe_estimado(minutos_totales: int, tarifa: Tarifa) -> float:
    minutos_restantes = minutos_totales
    total = 0.0

    minutos_dia = 1440
    minutos_medio_dia = 720
    minutos_hora = 60
    minutos_fraccion = 30

    tarifa_diario = float(tarifa.diario or 0)
    tarifa_medio_dia = float(tarifa.medio_dia or 0)
    tarifa_hora = float(tarifa.hora or 0)
    tarifa_fraccion = float(tarifa.fraccion or 0)

    dias = minutos_restantes // minutos_dia
    total += dias * tarifa_diario
    minutos_restantes -= dias * minutos_dia

    medios_dias = minutos_restantes // minutos_medio_dia
    total += medios_dias * tarifa_medio_dia
    minutos_restantes -= medios_dias * minutos_medio_dia

    if minutos_restantes > 0:
        if minutos_restantes <= minutos_hora:
            total += tarifa_hora
        else:
            total += tarifa_hora
            minutos_restantes -= minutos_hora

            horas_completas = minutos_restantes // minutos_hora
            total += horas_completas * tarifa_hora
            minutos_restantes -= horas_completas * minutos_hora

            if 0 < minutos_restantes <= minutos_fraccion:
                total += tarifa_fraccion
            elif minutos_restantes > minutos_fraccion:
                total += tarifa_hora

    return round(total, 2)


@router.get("/public/estado/{placa}")
def estado_vehiculo_publico(
    placa: str,
    db: Session = Depends(get_db),
):
    placa_normalizada = _normalizar_placa(placa)

    registro = (
        db.query(CurrentEstacionamiento)
        .filter(func.upper(CurrentEstacionamiento.placa) == placa_normalizada)
        .first()
    )

    if not registro:
        raise HTTPException(
            status_code=404,
            detail=f"No hay un vehiculo activo en el estacionamiento para la placa {placa_normalizada}",
        )

    tarifa = db.query(Tarifa).filter(Tarifa.id == registro.tarifa_id).first()
    minutos_transcurridos = None
    monto_estimado = None

    if tarifa:
        try:
            minutos_transcurridos = _minutos_transcurridos(registro.fecha_entrada, registro.hora_entrada)
            monto_estimado = _calcular_importe_estimado(minutos_transcurridos, tarifa)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "activo": True,
        "placa": registro.placa,
        "tarifa": {
            "media_hora": float(tarifa.fraccion) if tarifa and tarifa.fraccion is not None else None,
            "hora": float(tarifa.hora) if tarifa and tarifa.hora is not None else None,
            "medio_dia": float(tarifa.medio_dia) if tarifa and tarifa.medio_dia is not None else None,
            "dia": float(tarifa.diario) if tarifa and tarifa.diario is not None else None,
        },
        "minutos_transcurridos": minutos_transcurridos,
        "monto_estimado": monto_estimado,
        "fecha_entrada": registro.fecha_entrada.isoformat() if registro.fecha_entrada else None,
        "hora_entrada": registro.hora_entrada.strftime("%H:%M:%S") if registro.hora_entrada else None,
        "updated_at": registro.updated_at.isoformat() if registro.updated_at else None,
    }


@router.get("/public/estado/{placa}/view")
def estado_vehiculo_publico_view(
    request: Request,
    placa: str,
    db: Session = Depends(get_db),
):
    placa_normalizada = _normalizar_placa(placa)

    registro = (
        db.query(CurrentEstacionamiento)
        .filter(func.upper(CurrentEstacionamiento.placa) == placa_normalizada)
        .first()
    )

    tarifa = None
    minutos_transcurridos = None
    monto_estimado = None

    if registro:
        tarifa = db.query(Tarifa).filter(Tarifa.id == registro.tarifa_id).first()
        if tarifa:
            try:
                minutos_transcurridos = _minutos_transcurridos(registro.fecha_entrada, registro.hora_entrada)
                monto_estimado = _calcular_importe_estimado(minutos_transcurridos, tarifa)
            except ValueError:
                minutos_transcurridos = None
                monto_estimado = None

    return templates.TemplateResponse(
        "estado_publico.html",
        {
            "request": request,
            "placa_buscada": placa_normalizada,
            "registro": registro,
            "tarifa": tarifa,
            "minutos_transcurridos": minutos_transcurridos,
            "monto_estimado": monto_estimado,
        },
    )
