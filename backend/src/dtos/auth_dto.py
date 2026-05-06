from pydantic import BaseModel


class LoginDTO(BaseModel):
    email: str
    password: str


class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PinDTO(BaseModel):
    pin: str