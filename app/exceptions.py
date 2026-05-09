"""
Domain exceptions.

Raise these in the `services/` layer. The global handler in `main.py`
converts them to HTTP responses — services must NOT import HTTPException.
"""


class DomainError(Exception):
    """Base class for all domain exceptions in this service."""

    status_code: int = 400
    code: str = "domain_error"

    def __init__(self, message: str = "") -> None:
        super().__init__(message or self.__class__.__name__)
        self.message = message or self.__class__.__name__


class NotFound(DomainError):
    status_code = 404
    code = "not_found"


class Conflict(DomainError):
    status_code = 409
    code = "conflict"


class ValidationError(DomainError):
    status_code = 422
    code = "validation_error"


class IntegrationError(DomainError):
    """Failure calling an external service (HTTP, queue, webhook)."""

    status_code = 502
    code = "integration_error"
