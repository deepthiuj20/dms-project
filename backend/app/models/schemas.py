"""
Pydantic models and schemas for request/response validation
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ==================== Authentication ====================

class UserRole(str, Enum):
    """User roles"""
    ADMIN = "ADMIN"
    USER = "USER"


class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=12)
    given_name: str = Field(..., min_length=1, max_length=100)
    family_name: str = Field(..., min_length=1, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        if not any(c in '!@#$%^&*' for c in v):
            raise ValueError('Password must contain special character')
        return v


class LoginRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserInfo(BaseModel):
    """User information"""
    user_id: str
    email: str
    given_name: str
    family_name: str
    role: UserRole
    created_at: datetime
    email_verified: bool


# ==================== Documents ====================

class FileStatus(str, Enum):
    """File status"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class DocumentMetadata(BaseModel):
    """Document metadata"""
    document_id: str
    filename: str
    file_size: int
    mime_type: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    status: FileStatus
    tags: List[str] = []


class DocumentResponse(BaseModel):
    """Document response"""
    document_id: str
    filename: str
    file_size: int
    mime_type: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    status: FileStatus
    version_count: int
    tags: List[str] = []
    download_url: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Document list response"""
    documents: List[DocumentResponse]
    total: int
    skip: int
    limit: int


class InitiateUploadRequest(BaseModel):
    """Initiate file upload request"""
    filename: str = Field(..., min_length=1, max_length=255)
    file_size: int = Field(..., gt=0)
    mime_type: str
    tags: List[str] = []


class InitiateUploadResponse(BaseModel):
    """Initiate upload response with presigned URL"""
    document_id: str
    presigned_url: str
    expires_in: int


class CompleteUploadRequest(BaseModel):
    """Complete file upload request"""
    document_id: str
    file_key: str


class DocumentVersion(BaseModel):
    """Document version information"""
    version_id: str
    document_id: str
    created_at: datetime
    created_by: str
    file_size: int
    change_description: Optional[str] = None
    download_url: Optional[str] = None


class DocumentVersionsResponse(BaseModel):
    """Document versions response"""
    document_id: str
    versions: List[DocumentVersion]
    total: int


class SearchRequest(BaseModel):
    """Search request"""
    query: str = Field(..., min_length=1)
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
    tags: Optional[List[str]] = None
    status: Optional[FileStatus] = None


class UpdateDocumentRequest(BaseModel):
    """Update document request"""
    filename: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[FileStatus] = None


# ==================== Audit Log ====================

class AuditAction(str, Enum):
    """Audit log actions"""
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
    DELETE = "DELETE"
    UPDATE = "UPDATE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class AuditLogEntry(BaseModel):
    """Audit log entry"""
    event_id: str
    user_id: str
    action: AuditAction
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: str
    status: str  # SUCCESS, FAILURE
    details: dict


class AuditLogResponse(BaseModel):
    """Audit log response"""
    logs: List[AuditLogEntry]
    total: int
    skip: int
    limit: int


# ==================== Error Response ====================

class ErrorResponse(BaseModel):
    """Error response"""
    error_code: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
