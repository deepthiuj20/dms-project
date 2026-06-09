"""
Custom exception classes for the application
"""


class DMSException(Exception):
    """Base exception for DMS application"""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class AuthenticationException(DMSException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR")


class AuthorizationException(DMSException):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403, error_code="AUTHORIZATION_ERROR")


class ValidationException(DMSException):
    """Raised when validation fails"""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")


class ResourceNotFoundException(DMSException):
    """Raised when resource is not found"""
    
    def __init__(self, resource: str = "Resource"):
        message = f"{resource} not found"
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class ConflictException(DMSException):
    """Raised when resource already exists"""
    
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409, error_code="CONFLICT")


class S3Exception(DMSException):
    """Raised when S3 operation fails"""
    
    def __init__(self, message: str = "S3 operation failed"):
        super().__init__(message, status_code=500, error_code="S3_ERROR")


class DynamoDBException(DMSException):
    """Raised when DynamoDB operation fails"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500, error_code="DATABASE_ERROR")


class CognitoException(DMSException):
    """Raised when Cognito operation fails"""
    
    def __init__(self, message: str = "Cognito operation failed"):
        super().__init__(message, status_code=500, error_code="COGNITO_ERROR")


class InternalServerException(DMSException):
    """Raised for unexpected server errors"""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500, error_code="INTERNAL_ERROR")
