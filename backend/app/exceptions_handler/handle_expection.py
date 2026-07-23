from typing import Optional

class DataLabExceptionHandler(Exception):
    """Base exception for all DataLab application errors."""

    def __init__(self, detail: Optional[str] = None, status_code: int = 400):
        self.detail = detail or self.__class__.__doc__ or "An error occurred."
        self.status_code = status_code
        super().__init__(self.detail)


class ClientNotAuthorized(DataLabExceptionHandler):
    """Unauthorized access. Please login or provide valid credentials."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(detail or "Unauthorized access.", status_code=401)


class AccessDenied(DataLabExceptionHandler):
    """Access denied. The client is not permitted to perform this action."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(detail or "Access denied.", status_code=403)


class DatasetNotFound(DataLabExceptionHandler):
    """The requested dataset was not found."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(detail or "Dataset not found.", status_code=404)


class UserNotFound(DataLabExceptionHandler):
    """The requested user could not be located."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(detail or "User not found.", status_code=404)


class InvalidCredentials(DataLabExceptionHandler):
    """Invalid username or password was provided."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(detail or "Invalid credentials.", status_code=401)


class TokenInvalid(DataLabExceptionHandler):
    """The provided authentication token is invalid."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(detail or "Invalid token.", status_code=401)


class TokenExpired(DataLabExceptionHandler):
    """The authentication token has expired."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(detail or "Token has expired.", status_code=401)


class ValidationError(DataLabExceptionHandler):
    """A validation error occurred while processing request data."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(detail or "Validation error.", status_code=422)


class StorageLimitExceeded(DataLabExceptionHandler):
    """The user has exceeded their storage quota."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(detail or "Storage limit exceeded.", status_code=403)


class DataProcessingError(DataLabExceptionHandler):
    """An error occurred while processing dataset operations."""

    def __init__(self, detail: Optional[str] = None):
        super().__init__(detail or "Data processing error.", status_code=500)
