from sqlalchemy.orm import Session

from src.db.models import Contenido, Cuenta, Perfil
from src.db.models.user_model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, password_hash: str, age: int) -> User:
        user = User(email=email, password_hash=password_hash, age=age)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def find_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def find_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def list_all(self) -> list[User]:
        return self.db.query(User).all()

    def update(self, user_id: int, **fields) -> User | None:
        user = self.find_by_id(user_id)
        if not user:
            return None

        for key, value in fields.items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.find_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True


class CuentaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, plan: str, pin: str | None = None) -> Cuenta:
        cuenta = Cuenta(email=email, plan=plan, pin=pin)
        self.db.add(cuenta)
        self.db.commit()
        self.db.refresh(cuenta)
        return cuenta

    def find_by_id(self, cuenta_id: int) -> Cuenta | None:
        return self.db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()

    def find_by_email(self, email: str) -> Cuenta | None:
        return self.db.query(Cuenta).filter(Cuenta.email == email).first()

    def list_all(self) -> list[Cuenta]:
        return self.db.query(Cuenta).all()

    def update(self, cuenta_id: int, **fields) -> Cuenta | None:
        cuenta = self.find_by_id(cuenta_id)
        if not cuenta:
            return None

        for key, value in fields.items():
            setattr(cuenta, key, value)

        self.db.commit()
        self.db.refresh(cuenta)
        return cuenta

    def delete(self, cuenta_id: int) -> bool:
        cuenta = self.find_by_id(cuenta_id)
        if not cuenta:
            return False

        self.db.delete(cuenta)
        self.db.commit()
        return True


class PerfilRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        cuenta_id: int,
        nombre: str,
        es_infantil: bool = False,
        avatar: str | None = None,
    ) -> Perfil:
        perfil = Perfil(
            cuenta_id=cuenta_id,
            nombre=nombre,
            es_infantil=es_infantil,
            avatar=avatar,
        )
        self.db.add(perfil)
        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def find_by_id(self, perfil_id: int) -> Perfil | None:
        return self.db.query(Perfil).filter(Perfil.id == perfil_id).first()

    def list_by_cuenta(self, cuenta_id: int) -> list[Perfil]:
        return self.db.query(Perfil).filter(Perfil.cuenta_id == cuenta_id).all()

    def update(self, perfil_id: int, **fields) -> Perfil | None:
        perfil = self.find_by_id(perfil_id)
        if not perfil:
            return None

        for key, value in fields.items():
            setattr(perfil, key, value)

        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def delete(self, perfil_id: int) -> bool:
        perfil = self.find_by_id(perfil_id)
        if not perfil:
            return False

        self.db.delete(perfil)
        self.db.commit()
        return True

    def add_to_mi_lista(self, perfil_id: int, contenido_id: int) -> Perfil | None:
        perfil = self.find_by_id(perfil_id)
        contenido = self.db.query(Contenido).filter(Contenido.id == contenido_id).first()

        if not perfil or not contenido:
            return None

        if contenido not in perfil.mi_lista:
            perfil.mi_lista.append(contenido)
            self.db.commit()
            self.db.refresh(perfil)

        return perfil

    def remove_from_mi_lista(self, perfil_id: int, contenido_id: int) -> Perfil | None:
        perfil = self.find_by_id(perfil_id)
        if not perfil:
            return None

        perfil.mi_lista = [
            contenido for contenido in perfil.mi_lista
            if contenido.id != contenido_id
        ]

        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def get_mi_lista(self, perfil_id: int) -> list[Contenido]:
        perfil = self.find_by_id(perfil_id)
        if not perfil:
            return []

        return perfil.mi_lista