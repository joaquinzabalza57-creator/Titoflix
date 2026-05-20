class AppError(Exception):                                      # Clase base para todas las excepciones de la app
    status_code: int = 500                                      # Código HTTP por defecto (Internal Server Error)
    message: str = "Internal error"                             # Mensaje de error por defecto

    def __init__(self, message: str | None = None):             # Constructor de la excepción
        if message:                                             # Si se proporciona un mensaje personalizado
            self.message = message                              # Se sobrescribe el mensaje base

        super().__init__(self.message)                          # Inicializa la clase base de Python


class BadRequestError(AppError):                                # Error para peticiones mal formadas
    status_code = 400                                           # Código HTTP 400
    message = "Bad request"                                     # Mensaje: Petición incorrecta


class UnauthorizedError(AppError):                              # Error para falta de credenciales
    status_code = 401                                           # Código HTTP 401
    message = "Unauthorized"                                    # Mensaje: No autorizado


class ForbiddenError(AppError):                                 # Error para falta de permisos (ej. Control Parental)
    status_code = 403                                           # Código HTTP 403
    message = "Forbidden"                                       # Mensaje: Prohibido


class NotFoundError(AppError):                                  # Error para recursos que no existen
    status_code = 404                                           # Código HTTP 404
    message = "Resource not found"                              # Mensaje: Recurso no encontrado


class ConflictError(AppError):                                  # Error para conflictos de lógica (ej. Email duplicado)
    status_code = 409                                           # Código HTTP 409
    message = "Conflict"                                        # Mensaje: Conflicto


class ValidationError(AppError):                                # Error para fallos de esquema o datos inválidos
    status_code = 422                                           # Código HTTP 422
    message = "Validation error"                                # Mensaje: Error de validación