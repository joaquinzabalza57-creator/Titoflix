from passlib.context import CryptContext


# Bcrypt limita passwords a 72 bytes; los schemas aplican ese maximo antes.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Genera un hash seguro para passwords y PINs."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Compara texto plano con un hash almacenado."""
    return pwd_context.verify(plain, hashed)
