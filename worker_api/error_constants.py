"""
Error message constants used throughout the worker API application.
"""

# Authentication Errors
INVALID_TOKEN = "Invalid authentication token"
EXPIRED_TOKEN = "Authentication token has expired"
MISSING_TOKEN = "Authentication token is required"
UNAUTHORIZED_ACCESS = "You are not authorized to perform this action"

# Validation Errors
INVALID_INPUT = "Invalid input data"
MISSING_REQUIRED_FIELD = "Required field is missing"
INVALID_FILE_FORMAT = "Invalid file format"
FILE_TOO_LARGE = "File size exceeds maximum allowed size"

# Database Errors
DATABASE_ERROR = "Database operation failed"
RECORD_NOT_FOUND = "Record not found"
DUPLICATE_RECORD = "Record already exists"

# General Errors
INTERNAL_SERVER_ERROR = "An internal server error occurred"
SERVICE_UNAVAILABLE = "Service temporarily unavailable"
OPERATION_FAILED = "Operation failed"
