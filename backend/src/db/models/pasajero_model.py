from sqlalchemy import Column, Integer, String

from src.db.connection import Base


class Pasajero(Base):
    __tablename__ = "pasajeros"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telefono = Column(String, nullable=False)

