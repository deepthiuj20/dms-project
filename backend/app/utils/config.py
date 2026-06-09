"""
Configuration management for DMS application
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Document Management System"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"
    
    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_endpoint_url: Optional[str] = None  # For LocalStack
    
    # S3 Configuration
    s3_bucket_name: str
    s3_presigned_url_expiration: int = 3600  # 1 hour
    s3_encryption_type: str = "AES256"
    s3_max_file_size: int = 5368709120  # 5GB
    
    # DynamoDB Configuration
    dynamodb_documents_table: str = "dms_documents"
    dynamodb_versions_table: str = "dms_versions"
    dynamodb_audit_log_table: str = "dms_audit_logs"
    dynamodb_read_capacity: int = 10
    dynamodb_write_capacity: int = 10
    
    # Cognito Configuration
    cognito_user_pool_id: str
    cognito_client_id: str
    cognito_client_secret: Optional[str] = None
    cognito_region: str = "us-east-1"
    cognito_domain: Optional[str] = None
    
    # JWT Configuration
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # API Configuration
    api_gateway_url: Optional[str] = None
    allowed_origins: list = ["http://localhost:4200", "https://yourdomain.com"]
    allowed_methods: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: list = ["Content-Type", "Authorization"]
    
    # File Upload
    file_upload_chunk_size: int = 1024 * 1024  # 1MB
    allowed_file_types: list = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "image/jpeg",
        "image/png",
    ]
    
    # Security
    rate_limit_requests: int = 10000
    rate_limit_window: int = 60  # seconds
    enable_cors: bool = True
    enable_xray: bool = False
    
    # Logging
    cloudwatch_log_group: str = "/aws/lambda/dms"
    enable_request_logging: bool = True
    enable_response_logging: bool = False  # Don't log responses for security
    
    # Email Configuration
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    support_email: str = "support@yourdomain.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment.lower() == "development"


# Load settings from environment
settings = Settings()
