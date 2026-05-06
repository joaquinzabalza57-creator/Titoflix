from pydantic import BaseModel          # Base para definir DTOs con validación


class LoginDTO(BaseModel):
    email: str                          # Email del usuario (sin validación estricta como EmailStr)
    password: str                       # Contraseña del usuario

class TokenDTO(BaseModel):
    access_token: str                   # Token JWT generado tras autenticación
    token_type: str = "bearer"          # Tipo de token (usado en el header Authorization)
# * JWT significa JSON Web Token.

class PinDTO(BaseModel):
    pin: str                            # PIN del usuario (sin validaciones adicionales aquí)