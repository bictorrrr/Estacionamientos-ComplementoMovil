from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os

from dotenv import load_dotenv

from app.routes import auth
from app.routes import user
from app.routes import tarifa
from app.routes import turnos
from app.routes import mensaje
from app.routes import public


from .routes import dashboard

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "si", "sí"}


def _get_required_session_secret() -> str:
    """Require a strong session secret from environment variables."""
    secret = os.getenv("SESSION_SECRET_KEY", "").strip()
    if not secret:
        raise RuntimeError("Missing SESSION_SECRET_KEY environment variable")
    if len(secret) < 32:
        raise RuntimeError("SESSION_SECRET_KEY must be at least 32 characters long")
    return secret


def _get_session_https_only() -> bool:
    """Use secure cookies in production/Railway and allow HTTP during local development."""
    prod_default = bool(os.getenv("RAILWAY_ENVIRONMENT")) or os.getenv("APP_ENV", "").strip().lower() == "production"
    return _env_bool("SESSION_HTTPS_ONLY", default=prod_default)


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=_get_required_session_secret(),
    same_site="lax",
    https_only=_get_session_https_only(),
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/login", status_code=302)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tarifa.router)
app.include_router(turnos.router)
app.include_router(user.router)
app.include_router(mensaje.router)
app.include_router(public.router)