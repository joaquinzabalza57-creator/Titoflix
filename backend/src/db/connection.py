from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config.env import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """Dependency de FastAPI: abre una sesión por request y la cierra al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# FUNCIONES ÚTILES PARA DESARROLLO
# ============================================================================

def create_tables():
    """Crea todas las tablas en la BD (útil para inicialización)."""
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")


def drop_tables():
    """Elimina todas las tablas (⚠️ PELIGROSO - borra datos)."""
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Todas las tablas eliminadas")


def reset_database():
    """Reinicia la BD: elimina y recrea todas las tablas."""
    drop_tables()
    create_tables()