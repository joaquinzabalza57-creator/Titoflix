from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Configuracion central leida desde `.env` con valores seguros para desarrollo."""

    APP_NAME: str = "Titoflix API"              # Nombre visible de la aplicacion.
    ENVIRONMENT: str = "development"            # Entorno actual: development, production, etc.

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/titoflix"  # Conexion SQLAlchemy.

    HOST: str = "127.0.0.1"                     # Host donde escucha Uvicorn.
    PORT: int = 8000                            # Puerto HTTP del backend.
    HOST_IP: str = "127.0.0.1"                  # IP usada por Docker Manager y CORS en red local.

    JWT_SECRET: str = "cambiame-en-produccion"  # Clave privada para firmar tokens JWT.
    JWT_ALGORITHM: str = "HS256"                # Algoritmo de firma para JWT.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60       # Duracion de tokens de cuenta y media.

    # MinIO/S3 guarda videos, portadas, miniaturas y avatares fuera de Postgres.
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_PUBLIC_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "titoflix"
    S3_SECRET_KEY: str = "titoflix-secret"
    S3_BUCKET_NAME: str = "titoflix-media"
    S3_REGION: str = "us-east-1"
    S3_MEDIA_PREFIX: str = "media"
    S3_ASSETS_PREFIX: str = "assets"

    # Frontends autorizados para consumir la API desde navegador.
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # Credenciales del administrador sembrado automaticamente en desarrollo.
    ADMIN_USERNAME: str = "titoflix-admin"
    ADMIN_PASSWORD: str = "admin1234"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instancia compartida por routers, servicios y scripts de arranque.
settings = Settings()
