from pydantic_settings import BaseSettings, SettingsConfigDict  # Herramientas para manejar variables de entorno
import os


class Settings(BaseSettings):
    APP_NAME: str = "Titoflix API"              # Nombre de la aplicación
    ENVIRONMENT: str = "development"            # Entorno (development, production, etc.)

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/titoflix")  # URL de conexión

    HOST: str = os.getenv("HOST", "127.0.0.1")                  # Host local donde escucha Uvicorn
    PORT: int = int(os.getenv("PORT", "8000"))                            # Puerto donde corre la app

    JWT_SECRET: str = os.getenv("JWT_SECRET", "cambiame-en-produccion")   # Clave secreta para firmar tokens JWT
    JWT_ALGORITHM: str = "HS256"                # Algoritmo de encriptación para JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60       # Tiempo de expiración del token (en minutos)

    model_config = SettingsConfigDict(
        extra="ignore",                         # Ignora variables extra no definidas en la clase
    )

#JWT significa JSON Web Token. Es una forma de identificar usuarios de manera segura en aplicaciones

settings = Settings()                           # Crea una instancia con todas las configuraciones cargadas
