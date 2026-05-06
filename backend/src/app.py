from fastapi import FastAPI, Request

from src.middlewares.error_middleware import app_error_handler
from src.routers import auth_router, product_router, user_router
from src.utils.errors import AppError


app = FastAPI(title="Titoflix API")

async def app_error_handler_wrapper(request: Request, exc: Exception):
    if isinstance(exc, AppError):
        return await app_error_handler(request, exc)
    raise exc

app.add_exception_handler(AppError, app_error_handler_wrapper)

app.include_router(auth_router.router, prefix="/api")
app.include_router(user_router.router, prefix="/api")
app.include_router(product_router.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
