"""
Input validation utilities
"""
from typing import List
import os
from app.utils.exceptions import ValidationException
from app.utils.config import settings


def validate_file_size(file_size: int) -> None:
    """Validate file size"""
    if file_size > settings.s3_max_file_size:
        raise ValidationException(
            f"File size exceeds maximum allowed size of {settings.s3_max_file_size / (1024**3):.2f}GB"
        )
    if file_size <= 0:
        raise ValidationException("File size must be greater than 0")


def validate_file_type(mime_type: str) -> None:
    """Validate file MIME type"""
    if mime_type not in settings.allowed_file_types:
        raise ValidationException(
            f"File type {mime_type} is not allowed. Allowed types: {', '.join(settings.allowed_file_types)}"
        )


def validate_filename(filename: str) -> None:
    """Validate filename for security"""
    if not filename or len(filename.strip()) == 0:
        raise ValidationException("Filename cannot be empty")
    
    if len(filename) > 255:
        raise ValidationException("Filename too long (max 255 characters)")
    
    # Prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValidationException("Invalid filename")


def validate_email(email: str) -> None:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationException(f"Invalid email format: {email}")


def validate_uuid(uuid_value: str) -> None:
    """Validate UUID format"""
    import uuid
    try:
        uuid.UUID(uuid_value)
    except ValueError:
        raise ValidationException(f"Invalid UUID format: {uuid_value}")


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        raise ValidationException("Value must be a string")
    
    # Remove null bytes and other dangerous characters
    sanitized = value.replace('\x00', '').strip()
    
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_pagination(skip: int, limit: int) -> None:
    """Validate pagination parameters"""
    if skip < 0:
        raise ValidationException("skip must be >= 0")
    
    if limit <= 0 or limit > 100:
        raise ValidationException("limit must be between 1 and 100")
