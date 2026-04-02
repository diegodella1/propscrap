from __future__ import annotations


class AppError(Exception):
    status_code = 500

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class ValidationError(AppError):
    status_code = 422


class AuthenticationError(AppError):
    status_code = 401


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class ConfigurationError(AppError):
    status_code = 503


class ExternalServiceError(AppError):
    status_code = 502
