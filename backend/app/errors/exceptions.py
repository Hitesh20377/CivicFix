class CivicFixException(Exception):
    """Base exception for CivicFix application."""
    status_code = 500
    error_code = 'INTERNAL_ERROR'

    def __init__(self, message, status_code=None, error_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['error_code'] = self.error_code
        rv['success'] = False
        return rv

class ValidationError(CivicFixException):
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, error_code='VALIDATION_ERROR', payload=payload)

class AuthenticationError(CivicFixException):
    def __init__(self, message="Authentication required"):
        super().__init__(message, status_code=401, error_code='UNAUTHORIZED')

class AuthorizationError(CivicFixException):
    def __init__(self, message="Permission denied"):
        super().__init__(message, status_code=403, error_code='FORBIDDEN')

class ResourceNotFoundError(CivicFixException):
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404, error_code='RESOURCE_NOT_FOUND')

class DatabaseError(CivicFixException):
    def __init__(self, message="Database operation failed"):
        super().__init__(message, status_code=500, error_code='DATABASE_ERROR')

class RateLimitError(CivicFixException):
    def __init__(self, message="Too many requests"):
        super().__init__(message, status_code=429, error_code='RATE_LIMIT_EXCEEDED')
