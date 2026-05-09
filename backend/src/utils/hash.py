from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    if pwd_context.identify(hashed) is None:
        return plain == hashed

    return pwd_context.verify(plain, hashed)
