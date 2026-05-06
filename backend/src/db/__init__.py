# ============================================================================
# IMPORTS DE CONEXIÓN Y SESIONES
# ============================================================================
from .connection import Base, get_db, engine, SessionLocal

# ============================================================================
# IMPORTS DE TODOS LOS MODELOS
# ============================================================================
from .models import (
    Cuenta,
    Perfil,
    Genero,
    Contenido,
    Temporada,
    Episodio,
    Vista,
    Calificacion,
    contenido_generos,
    mi_lista,
)

# ============================================================================
# EXPORTS (para que sea fácil importar desde cualquier lado)
# ============================================================================
__all__ = [
    # Conexión
    "Base",
    "get_db", 
    "engine",
    "SessionLocal",
    
    # Modelos
    "Cuenta",
    "Perfil", 
    "Genero",
    "Contenido",
    "Temporada",
    "Episodio",
    "Vista",
    "Calificacion",
    "contenido_generos",
    "mi_lista",
]