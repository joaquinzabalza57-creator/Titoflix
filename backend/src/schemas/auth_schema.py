from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PinSchema(BaseModel):
    pin: str = Field(min_length=4, max_length=8)


class PerfilAuthSchema(BaseModel):
    authorization: str | None = None
    pin: str | None = Field(default=None, min_length=4, max_length=8)
