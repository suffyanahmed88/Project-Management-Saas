class AppError(Exception):
    def __init__(self, status_code: int, message: str, code: str = "error"):
        self.status_code = status_code
        self.message = message
        self.code = code


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(404, message, "not_found")


class ForbiddenError(AppError):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(403, message, "forbidden")


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict"):
        super().__init__(409, message, "conflict")


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(401, message, "unauthorized")


class ValidationErrorApp(AppError):
    def __init__(self, message: str = "Invalid input"):
        super().__init__(422, message, "validation_error")
