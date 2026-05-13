from fastapi import FastAPI                                     # Importa el framework FastAPI

from src.middlewares import app_error_handler                   # Importa el manejador global de errores
from src.routers import auth_router, product_router, user_router # Importa los routers de la API
from src.utils.errors import AppError                           # Importa la excepción base de la app


API_PREFIX = "/api/v1"                                          # Define el prefijo de versión de la API

app = FastAPI(title="Titoflix API", version="1.0.0")            # Inicializa la aplicación FastAPI

app.add_exception_handler(AppError, app_error_handler)          # Registra el middleware de errores

app.include_router(auth_router.router, prefix=API_PREFIX)       # Incluye rutas de autenticación
app.include_router(user_router.router, prefix=API_PREFIX)       # Incluye rutas de usuarios y perfiles
app.include_router(product_router.router, prefix=API_PREFIX)    # Incluye rutas de catálogo y productos


@app.get("/health")                                             # Define endpoint de verificación de estado
def health():                                                   # Función de chequeo de salud
    return {"status": "ok"}                                     # Retorna estado exitoso
