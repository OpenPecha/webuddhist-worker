import pytest

from worker_api.error_constants import (
    INVALID_TOKEN,
    EXPIRED_TOKEN,
    MISSING_TOKEN,
    UNAUTHORIZED_ACCESS,
    INVALID_INPUT,
    MISSING_REQUIRED_FIELD,
    INVALID_FILE_FORMAT,
    FILE_TOO_LARGE,
    DATABASE_ERROR,
    RECORD_NOT_FOUND,
    DUPLICATE_RECORD,
    INTERNAL_SERVER_ERROR,
    SERVICE_UNAVAILABLE,
    OPERATION_FAILED,
)


def test_authentication_error_constants():
    assert INVALID_TOKEN == "Invalid authentication token"
    assert EXPIRED_TOKEN == "Authentication token has expired"
    assert MISSING_TOKEN == "Authentication token is required"
    assert UNAUTHORIZED_ACCESS == "You are not authorized to perform this action"


def test_validation_error_constants():
    assert INVALID_INPUT == "Invalid input data"
    assert MISSING_REQUIRED_FIELD == "Required field is missing"
    assert INVALID_FILE_FORMAT == "Invalid file format"
    assert FILE_TOO_LARGE == "File size exceeds maximum allowed size"


def test_database_error_constants():
    assert DATABASE_ERROR == "Database operation failed"
    assert RECORD_NOT_FOUND == "Record not found"
    assert DUPLICATE_RECORD == "Record already exists"


def test_general_error_constants():
    assert INTERNAL_SERVER_ERROR == "An internal server error occurred"
    assert SERVICE_UNAVAILABLE == "Service temporarily unavailable"
    assert OPERATION_FAILED == "Operation failed"
