from sqlalchemy import create_engine                        # Función para crear la conexión a la Base de Datos
from sqlalchemy.orm import declarative_base, sessionmaker   # Base para modelos ORM y fábrica de sesiones

from src.config.env import settings               # Importa configuración (ej: DATABASE_URL)

engine = create_engine(settings.DATABASE_URL)     # Crea el engine de conexión usando la URL de la Base de Datos
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)  
# Configura las conexiones con la base de datos de las sesiones
Base = declarative_base()                         
# Clase base para definir los modelos ORM (Object Relational Mapping, usar los objetos en python directo en lugar de SQL directo)


def get_db():
    """Dependency de FastAPI: abre una sesión por request y la cierra al final."""
    db = SessionLocal()                           # Crea una nueva sesión de base de datos
    try:
        yield db                                  # Devuelve la sesión para usarla en el endpoint
    finally:
        db.close()                                # Cierra la sesión al finalizar el request

# ============================================================================
# FUNCIONES ÚTILES PARA DESARROLLO
# ============================================================================
def create_tables():
    """Crea todas las tablas en la BD (útil para inicialización)."""
    Base.metadata.create_all(bind=engine)        # Crea todas las tablas definidas en los modelos
    print("✅ Tablas creadas exitosamente")      # Mensaje de confirmación


def drop_tables():
    """Elimina todas las tablas (⚠️ PELIGROSO - borra datos)."""
    Base.metadata.drop_all(bind=engine)          # Elimina todas las tablas de la base de datos
    print("⚠️ Todas las tablas eliminadas")     # Mensaje de advertencia


def reset_database():
    """Reinicia la BD: elimina y recrea todas las tablas."""
    drop_tables()                                # Borra todas las tablas existentes
    create_tables()                              # Vuelve a crearlas desde cero