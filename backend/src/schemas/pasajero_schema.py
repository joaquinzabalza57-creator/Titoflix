from pydantic import BaseModel, EmailStr, Field


class CreatePasajeroSchema(BaseModel):
    nombre: str = Field(min_length=2)
    email: EmailStr
    telefono: str = Field(min_length=11)

class UpdatePasajeroSchema(BaseModel):
    nombre: str | None = Field(default=None, min_length=2)
    email: EmailStr | None = None
    telefono: str | None = Field(default=None, min_length=11)

class DeletePasajeroSchema(BaseModel):
    id: int

class GetPasajeroSchema(BaseModel):
    id: int