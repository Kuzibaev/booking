from typing import Optional

from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ErrorWrapper
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request


class PaymentError(Exception):
    def __init__(self, message, code=None, gateway_message=None):
        super().__init__(message)
        self.code = code
        self.gateway_message = gateway_message


class ObjectDoesNotExist(Exception):
    pass


class DatabaseException(Exception):
    pass


class DatabaseValidationError(DatabaseException):
    def __init__(self, message: str, field: Optional[str] = None) -> None:
        self.message = message
        self.field = field


async def database_validation_exception_handler(request: Request, exc: DatabaseValidationError) -> JSONResponse:
    return await request_validation_exception_handler(
        request,
        RequestValidationError([ErrorWrapper(ValueError(exc.message), exc.field or "__root__")]),
    )


def parse_sqlalchemy_exc(exception: SQLAlchemyError):
    if hasattr(exception, 'orig'):
        exc = str(exception.orig)
        if 'DETAIL:' in exc:
            return exc.split('DETAIL:')[1].strip()
    return 'Unhandled error'
