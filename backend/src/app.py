from fastapi import FastAPI

from src.middlewares import app_error_handler
from src.routers import auth_router, product_router, user_router
from src.utils import AppError


API_PREFIX = "/api/v1"

app = FastAPI(title="Titoflix API", version="1.0.0")

app.add_exception_handler(AppError, app_error_handler)

app.include_router(auth_router.router, prefix=API_PREFIX)
app.include_router(user_router.router, prefix=API_PREFIX)
app.include_router(product_router.router, prefix=API_PREFIX)


@app.get("/health")
def health():
    return {"status": "ok"}
