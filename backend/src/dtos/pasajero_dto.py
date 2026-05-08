from pydantic import BaseModel


class CreatePasajeroDTO(BaseModel): # POST
    nombre: str
    email: str
    telefono: str

class UpdatePasajeroDTO(BaseModel): # PUT/PATCH
    nombre: str | None = None
    email: str | None = None
    telefono: str | None = None

class DeletePasajeroDTO(BaseModel): # DELETE
    id: int

class GetPasajeroDTO(BaseModel): # GET (individual)
    id: int

class PasajeroResponseDTO(BaseModel):
    id: int
    nombre: str
    email: str
    telefono: str

    model_config = {"from_attributes": True}
