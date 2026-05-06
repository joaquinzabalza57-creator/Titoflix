from pydantic_settings import BaseSettings, SettingsConfigDict  # Herramientas para manejar variables de entorno


class Settings(BaseSettings):
    APP_NAME: str = "Titoflix API"              # Nombre de la aplicación
    ENVIRONMENT: str = "development"            # Entorno (development, production, etc.)

    DATABASE_URL: str                           # URL de conexión a la base de datos (obligatoria)

    PORT: int = 8000                            # Puerto donde corre la app

    JWT_SECRET: str                             # Clave secreta para firmar tokens JWT
    JWT_ALGORITHM: str = "HS256"                # Algoritmo de encriptación para JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60       # Tiempo de expiración del token (en minutos)

    model_config = SettingsConfigDict(
        env_file=".env",                        # Archivo desde donde se cargan las variables
        env_file_encoding="utf-8",              # Codificación del archivo .env
        extra="ignore",                         # Ignora variables extra no definidas en la clase
    )

#JWT significa JSON Web Token. Es una forma de identificar usuarios de manera segura en aplicaciones

settings = Settings()                           # Crea una instancia con todas las configuraciones cargadas
