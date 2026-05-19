from pathlib import Path
import sys

import uvicorn

# Permite ejecutar este archivo directamente con `python src/main.py` sin perder
# imports absolutos del paquete `src`.
if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import settings


if __name__ == "__main__":
    # Uvicorn importa `src.app:app`, asi se reutiliza la misma instancia en Docker
    # y en ejecucion local.
    uvicorn.run(
        "src.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )
