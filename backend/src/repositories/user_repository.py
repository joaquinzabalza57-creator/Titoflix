from sqlalchemy.orm import Session

from src.db.models import Contenido, Cuenta, Perfil
from src.db.models.user_model import User


class UserRepository:
    def __init__(self, db: Session):                                     # Inicializa el repositorio con la sesión de DB
        self.db = db

    def create(self, email: str, password_hash: str, age: int) -> User:  # Crea y persiste un nuevo usuario
        user = User(email=email, password_hash=password_hash, age=age)
        self.db.add(user)
        self.db.commit()                                                 # Guarda cambios en la base de datos
        self.db.refresh(user)                                            # Actualiza la instancia con datos de DB
        return user

    def find_by_id(self, user_id: int) -> User | None:                   # Busca usuario por ID
        return self.db.query(User).filter(User.id == user_id).first()

    def find_by_email(self, email: str) -> User | None:                  # Busca usuario por email
        return self.db.query(User).filter(User.email == email).first()

    def list_all(self) -> list[User]:                                    # Obtiene todos los registros de usuarios
        return self.db.query(User).all()

    def update(self, user_id: int, **fields) -> User | None:             # Actualiza campos dinámicamente
        user = self.find_by_id(user_id)                                  # Verifica existencia
        if not user:
            return None

        for key, value in fields.items():                                # Aplica cambios
            setattr(user, key, value)

        self.db.commit()                                                 # Persiste cambios
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:                              # Elimina un usuario por ID
        user = self.find_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)                                             # Elimina registro
        self.db.commit()                                                 # Confirma eliminación
        return True


class CuentaRepository:
    def __init__(self, db: Session):                                     # Inicializa el repositorio con la sesión de DB
        self.db = db

    def create(self, email: str, plan: str, pin: str | None = None) -> Cuenta: # Crea y persiste una nueva cuenta
        cuenta = Cuenta(email=email, plan=plan, pin=pin)
        self.db.add(cuenta)
        self.db.commit()                                                 # Guarda cambios en la base de datos
        self.db.refresh(cuenta)                                          # Actualiza la instancia con datos de DB
        return cuenta

    def find_by_id(self, cuenta_id: int) -> Cuenta | None:               # Busca cuenta por ID
        return self.db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()

    def find_by_email(self, email: str) -> Cuenta | None:                # Busca cuenta por email
        return self.db.query(Cuenta).filter(Cuenta.email == email).first()

    def list_all(self) -> list[Cuenta]:                                  # Obtiene todos los registros de cuentas
        return self.db.query(Cuenta).all()

    def update(self, cuenta_id: int, **fields) -> Cuenta | None:         # Actualiza campos dinámicamente
        cuenta = self.find_by_id(cuenta_id)                              # Verifica existencia
        if not cuenta:
            return None

        for key, value in fields.items():                                # Aplica cambios
            setattr(cuenta, key, value)

        self.db.commit()                                                 # Persiste cambios
        self.db.refresh(cuenta)
        return cuenta

    def delete(self, cuenta_id: int) -> bool:                            # Elimina una cuenta por ID
        cuenta = self.find_by_id(cuenta_id)
        if not cuenta:
            return False

        self.db.delete(cuenta)                                           # Elimina registro
        self.db.commit()                                                 # Confirma eliminación
        return True


class PerfilRepository:
    def __init__(self, db: Session):                                     # Inicializa el repositorio con la sesión de DB
        self.db = db

    def create(                                                         # Crea y persiste un nuevo perfil
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
        self.db.commit()                                                # Guarda cambios en la base de datos
        self.db.refresh(perfil)                                         # Actualiza la instancia con datos de DB
        return perfil

    def find_by_id(self, perfil_id: int) -> Perfil | None:              # Busca perfil por ID
        return self.db.query(Perfil).filter(Perfil.id == perfil_id).first()

    def list_by_cuenta(self, cuenta_id: int) -> list[Perfil]:           # Lista todos los perfiles de una cuenta
        return self.db.query(Perfil).filter(Perfil.cuenta_id == cuenta_id).all()

    def update(self, perfil_id: int, **fields) -> Perfil | None:        # Actualiza campos dinámicamente
        perfil = self.find_by_id(perfil_id)                             # Verifica existencia
        if not perfil:
            return None

        for key, value in fields.items():                               # Aplica cambios
            setattr(perfil, key, value)

        self.db.commit()                                                # Persiste cambios
        self.db.refresh(perfil)
        return perfil

    def delete(self, perfil_id: int) -> bool:                           # Elimina un perfil por ID
        perfil = self.find_by_id(perfil_id)
        if not perfil:
            return False

        self.db.delete(perfil)                                          # Elimina registro
        self.db.commit()                                                # Confirma eliminación
        return True

    def add_to_mi_lista(self, perfil_id: int, contenido_id: int) -> Perfil | None: # Agrega contenido a "Mi lista"
        perfil = self.find_by_id(perfil_id)
        contenido = self.db.query(Contenido).filter(Contenido.id == contenido_id).first()

        if not perfil or not contenido:
            return None

        if contenido not in perfil.mi_lista:                            # Evita duplicados
            perfil.mi_lista.append(contenido)
            self.db.commit()                                            # Persiste relación
            self.db.refresh(perfil)

        return perfil

    def remove_from_mi_lista(self, perfil_id: int, contenido_id: int) -> Perfil | None: # Elimina contenido de "Mi lista"
        perfil = self.find_by_id(perfil_id)
        if not perfil:
            return None

        perfil.mi_lista = [                                             # Filtra para quitar el contenido
            contenido for contenido in perfil.mi_lista
            if contenido.id != contenido_id
        ]

        self.db.commit()                                                # Persiste cambios
        self.db.refresh(perfil)
        return perfil

    def get_mi_lista(self, perfil_id: int) -> list[Contenido]:           # Obtiene la lista de contenidos
        perfil = self.find_by_id(perfil_id)
        if not perfil:
            return []

        return perfil.mi_lista