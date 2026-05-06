from pydantic import BaseModel, EmailStr, Field   # Herramientas para validar datos en FastAPI


class LoginSchema(BaseModel):
    email: EmailStr                               # Email válido (Pydantic lo valida automáticamente)
    password: str = Field(min_length=8)            # Contraseña con mínimo 8 caracteres


class TokenSchema(BaseModel):
    access_token: str                             # Token JWT generado al iniciar sesión
    token_type: str = "bearer"                    # Tipo de token (usado en Authorization header)


class PinSchema(BaseModel):
    pin: str = Field(min_length=4, max_length=4)   # PIN obligatorio de exactamente 4 caracteres