import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.db import create_tables
from src.middlewares import app_error_handler
from src.routers import asset_router, auth_router, product_router, user_router
from src.utils.errors import AppError


API_PREFIX = "/api/v1"

# Punto central de armado de FastAPI: aca se registran middlewares, routers y
# tareas de arranque que necesitan correr antes de aceptar requests.
app = FastAPI(title="Titoflix API", version="1.0.0", redirect_slashes=False)

# Origenes permitidos para el frontend. En desarrollo se suma HOST_IP para que
# una app abierta desde otro equipo de la red pueda consumir este backend.
allowed_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]
host_ip_origin = f"http://{settings.HOST_IP}:3000"
if settings.HOST_IP and host_ip_origin not in allowed_origins:
    allowed_origins.append(host_ip_origin)
allow_origin_regex = r"https?://.*" if settings.ENVIRONMENT == "development" else None

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)

# Todas las rutas funcionales viven bajo /api/v1 para que el frontend pueda
# cambiar de version sin mezclar endpoints antiguos y nuevos.
app.include_router(auth_router.router, prefix=API_PREFIX)
app.include_router(asset_router.router, prefix=API_PREFIX)
app.include_router(user_router.router, prefix=API_PREFIX)
app.include_router(product_router.router, prefix=API_PREFIX)


@app.on_event("startup")
def startup():
    """Prepara la base de datos al iniciar, esperando a Postgres si Docker aun levanta."""
    for attempt in range(1, 11):
        try:
            create_tables()
            return
        except Exception:
            if attempt == 10:
                raise
            time.sleep(2)


@app.get("/health")
def health():
    """Endpoint liviano para checks de Docker, proxies o monitoreo local."""
    return {"status": "ok"}
