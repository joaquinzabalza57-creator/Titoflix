class AppError(Exception):
    """Base comun para errores de negocio que deben convertirse en HTTP JSON."""

    status_code: int = 500
    message: str = "Internal error"

    def __init__(self, message: str | None = None):
        if message:
            self.message = message

        super().__init__(self.message)


class BadRequestError(AppError):
    """Peticion mal formada o imposible de interpretar."""

    status_code = 400
    message = "Bad request"


class UnauthorizedError(AppError):
    """Faltan credenciales o el token no es valido."""

    status_code = 401
    message = "Unauthorized"


class LockedError(AppError):
    """Recurso temporalmente bloqueado por seguridad."""

    status_code = 423
    message = "Locked"


class ForbiddenError(AppError):
    """El usuario esta autenticado, pero no tiene permisos para la accion."""

    status_code = 403
    message = "Forbidden"


class NotFoundError(AppError):
    """El recurso solicitado no existe."""

    status_code = 404
    message = "Resource not found"


class ConflictError(AppError):
    """La request es valida, pero viola una regla de negocio."""

    status_code = 409
    message = "Conflict"


class ValidationError(AppError):
    """Datos validos a nivel HTTP, pero invalidos para el dominio."""

    status_code = 422
    message = "Validation error"
