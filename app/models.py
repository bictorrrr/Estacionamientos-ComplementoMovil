from datetime import date, time, datetime
from sqlalchemy import DECIMAL, Date, Integer, Text, Time, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class CurrentEstacionamiento(Base):
    __tablename__ = "current_estacionamiento"

    id: Mapped[int] = mapped_column(primary_key=True)
    encargado_id: Mapped[int] = mapped_column(nullable=False)
    placa: Mapped[str] = mapped_column(String(100))
    tarifa_id: Mapped[int] = mapped_column(Integer)
    turno_id: Mapped[int] = mapped_column(Integer)
    fecha_entrada: Mapped[date] = mapped_column(Date())
    hora_entrada: Mapped[time] = mapped_column(Time())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[int] = mapped_column(unique=True, nullable=False)
    nombre: Mapped[str | None] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    comision: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0.00)
    rol: Mapped[str | None] = mapped_column(Text)
    observaciones: Mapped[str | None] = mapped_column(String(100))

class Tarifa(Base):
    __tablename__ = "tarifas"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_vehiculo: Mapped[str | None] = mapped_column(String(100))
    hora: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    fraccion: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    medio_dia: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    diario: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00)
    observaciones: Mapped[str | None] = mapped_column(String(255))
    eliminado: Mapped[int] = mapped_column(Integer, default=0)
    default: Mapped[int] = mapped_column(Integer, default=0) 

class Turno(Base):
    __tablename__ = "turnos"

    id: Mapped[int] = mapped_column(primary_key=True)
    encargado_id: Mapped[int] = mapped_column(nullable=False)
    fecha: Mapped[date] = mapped_column(Date())
    hora_inicio: Mapped[time] = mapped_column(Time())
    estado: Mapped[str] = mapped_column(String(100)) 
    hora_fin: Mapped[time] = mapped_column(Time())
    fecha_fin: Mapped[date] = mapped_column(Date())


class Mensaje(Base):
    __tablename__ = "mensajes"

    id: Mapped[int] = mapped_column(primary_key=True)
    turno_id: Mapped[int] = mapped_column(Integer, nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    admin_id: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str | None] = mapped_column(String(100), default="pendiente")
    fecha_enviado: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    

