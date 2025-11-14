from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


# Handle SQLAlchemy errors
async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError):
    """
    Handle SQLAlchemy errors.

    This exception handler catches any SQLAlchemy errors that occur during
    request processing, logs the error, and returns a 503 Service Unavailable
    response to the client.

    :param request: The current request object.
    :param exc: The SQLAlchemy error that occurred.
    :return: A JSONResponse object containing a 503 Service Unavailable response.
    """
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database service unavailable. Please try again later."},
    )


# Handle Integrity errors (e.g. unique constraint violations)
async def integrity_error_handler(
        request: Request, exc: IntegrityError):
    """
    Handle Integrity errors (e.g. unique constraint violations)

    This exception handler catches any Integrity errors that occur during
    request processing, logs the error, and returns a 400 Bad Request response
    to the client.

    :param request: The current request object.
    :param exc: The Integrity error that occurred.
    :return: A JSONResponse object containing a 400 Bad Request response.
    """
    logger.error(f"Integrity error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Invalid data or constraint violation."},
    )


# Handle validation errors (bad request data)
async def validation_exception_handler(
        request: Request, exc: RequestValidationError):
    """
    Handle validation errors (bad request data)

    This exception handler catches any validation errors that occur during
    request processing, logs the error, and returns a 422 Unprocessable Entity
    response to the client.

    :param request: The current request object.
    :param exc: The validation error that occurred.
    :return: A JSONResponse object containing a 422 Unprocessable Entity response.
    """
    # Make errors JSON serializable by converting ctx values to strings
    errors = []
    for error in exc.errors():
        error_dict = dict(error)
        if 'ctx' in error_dict:
            error_dict['ctx'] = {
                key: str(value) for key, value in error_dict['ctx'].items()}
        errors.append(error_dict)

    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": errors},
    )


# Handle generic HTTPExceptions (e.g. 401, 403, 404)
async def http_exception_handler(
        request: Request, exc: StarletteHTTPException):
    """
    Handle generic HTTPExceptions (e.g. 401, 403, 404)

    This exception handler catches any HTTPExceptions that occur during
    request processing, logs the error, and returns a JSONResponse object
    containing the error details.

    :param request: The current request object.
    :param exc: The HTTPException that occurred.
    :return: A JSONResponse object containing the error details.
    """
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Catch-all for any uncaught exceptions
async def generic_exception_handler(
        request: Request, exc: Exception):
    """
    Catch-all for any uncaught exceptions

    This exception handler catches any unexpected exceptions that occur during
    request processing, logs the error, and returns a 500 Internal Server Error
    response to the client.

    :param request: The current request object.
    :param exc: The unexpected exception that occurred.
    :return: A JSONResponse object containing a 500 Internal Server Error response.
    """
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred."},
    )
