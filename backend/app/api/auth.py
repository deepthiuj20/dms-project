"""
Authentication endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, UserInfo
)
from app.utils.logger import setup_logger
from app.utils.exceptions import AuthenticationException


router = APIRouter()
logger = setup_logger(__name__)


@router.post("/register", response_model=dict)
async def register(request: RegisterRequest):
    """
    User registration endpoint
    
    Integrates with AWS Cognito
    """
    try:
        # This would integrate with Cognito service in production
        logger.info(f"Registering user: {request.email}")
        
        return {
            "message": "Registration successful",
            "email": request.email,
        }
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    
    Returns JWT token
    """
    try:
        logger.info(f"Login attempt for: {request.email}")
        
        # This would integrate with Cognito service in production
        return TokenResponse(
            access_token="test-token",
            expires_in=3600,
            user={
                "user_id": "test-user",
                "email": request.email,
                "role": "USER",
            }
        )
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )


@router.post("/logout")
async def logout():
    """User logout endpoint"""
    logger.info("User logout")
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserInfo)
async def get_current_user():
    """Get current user information"""
    # This would extract user from JWT token in production
    return UserInfo(
        user_id="test-user",
        email="user@example.com",
        given_name="Test",
        family_name="User",
        role="USER",
        created_at="2024-01-01T00:00:00Z",
        email_verified=True,
    )


@router.post("/refresh-token")
async def refresh_token():
    """Refresh JWT token"""
    logger.info("Token refresh")
    return {
        "access_token": "new-token",
        "expires_in": 3600,
    }
