from sqlalchemy.orm import Session

from src.db.models import Contenido, Cuenta, Perfil


class CuentaRepository:
    """Capa de acceso a datos para cuentas."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, password_hash: str, plan: str, is_admin: bool = False) -> Cuenta:
        """Inserta una cuenta y devuelve la instancia refrescada."""
        cuenta = Cuenta(
            email=email,
            password_hash=password_hash,
            plan=plan,
            is_admin=is_admin,
        )
        self.db.add(cuenta)
        self.db.commit()
        self.db.refresh(cuenta)
        return cuenta

    def find_by_id(self, cuenta_id: int) -> Cuenta | None:
        """Busca cuenta por ID."""
        return self.db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()

    def find_by_email(self, email: str) -> Cuenta | None:
        """Busca cuenta por email, usado en login y validacion de duplicados."""
        return self.db.query(Cuenta).filter(Cuenta.email == email).first()

    def list_admins(self) -> list[Cuenta]:
        """Lista cuentas admin para el login administrativo por password."""
        return self.db.query(Cuenta).filter(Cuenta.is_admin.is_(True)).all()

    def list_all(self) -> list[Cuenta]:
        """Lista todas las cuentas para la consola admin."""
        return self.db.query(Cuenta).all()

    def update(self, cuenta_id: int, **fields) -> Cuenta | None:
        """Actualiza campos ya validados por la capa de servicio."""
        cuenta = self.find_by_id(cuenta_id)
        if not cuenta:
            return None

        for key, value in fields.items():
            setattr(cuenta, key, value)

        self.db.commit()
        self.db.refresh(cuenta)
        return cuenta

    def delete(self, cuenta_id: int) -> bool:
        """Elimina una cuenta si existe."""
        cuenta = self.find_by_id(cuenta_id)
        if not cuenta:
            return False

        self.db.delete(cuenta)
        self.db.commit()
        return True


class PerfilRepository:
    """Capa de acceso a datos para perfiles y sus relaciones."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        cuenta_id: int,
        nombre: str,
        pin: str | None = None,
        es_infantil: bool = False,
        avatar: str | None = None,
    ) -> Perfil:
        """Inserta un perfil dentro de una cuenta."""
        perfil = Perfil(
            cuenta_id=cuenta_id,
            nombre=nombre,
            pin=pin,
            es_infantil=es_infantil,
            avatar=avatar,
        )
        self.db.add(perfil)
        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def find_by_id(self, perfil_id: int) -> Perfil | None:
        """Busca perfil por ID."""
        return self.db.query(Perfil).filter(Perfil.id == perfil_id).first()

    def list_by_cuenta(self, cuenta_id: int) -> list[Perfil]:
        """Lista perfiles asociados a una cuenta."""
        return self.db.query(Perfil).filter(Perfil.cuenta_id == cuenta_id).all()

    def update(self, perfil_id: int, **fields) -> Perfil | None:
        """Actualiza campos ya validados por PerfilService."""
        perfil = self.find_by_id(perfil_id)
        if not perfil:
            return None

        for key, value in fields.items():
            setattr(perfil, key, value)

        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def delete(self, perfil_id: int) -> bool:
        """Elimina un perfil si existe."""
        perfil = self.find_by_id(perfil_id)
        if not perfil:
            return False

        self.db.delete(perfil)
        self.db.commit()
        return True

    def add_to_mi_lista(self, perfil_id: int, contenido_id: int) -> Perfil | None:
        """Agrega contenido a Mi lista evitando duplicados."""
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
        """Quita contenido de Mi lista si el perfil existe."""
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
        """Devuelve los contenidos guardados por el perfil."""
        perfil = self.find_by_id(perfil_id)
        if not perfil:
            return []

        return perfil.mi_lista
