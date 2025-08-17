from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload  # ADD joinedload import
from datetime import timedelta

from app.db.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash, verify_token
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (requires director approval)"""

    # Check if user already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Check if employee code exists
    if user_data.employee_code:
        existing_employee = db.query(User).filter(
            User.employee_code == user_data.employee_code
        ).first()
        if existing_employee:
            raise HTTPException(
                status_code=400,
                detail="Employee code already exists"
            )

    # Create user with PENDING_APPROVAL status
    db_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        employee_code=user_data.employee_code,
        phone_number=user_data.phone_number,
        department=user_data.department,
        designation=user_data.designation,
        status="PENDING_APPROVAL"
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """Login user and return access token"""

    # FIXED: Find user by email WITH role relationship loaded
    user = db.query(User).options(joinedload(User.role)).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is approved
    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account status: {user.status}. Please contact administrator.",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    user.failed_login_attempts = 0
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


# FIXED: Updated get_current_user function with proper role loading
async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user with role information"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Debug: Print token info
        print(f"Received token: {token[:20]}..." if token else "No token")

        email = verify_token(token)
        print(f"Extracted email: {email}")

        if email is None:
            print("Token verification failed")
            raise credentials_exception

        # FIXED: Load user WITH role relationship using joinedload
        user = db.query(User).options(joinedload(User.role)).filter(User.email == email).first()
        print(f"User found: {user is not None}")

        if user is None:
            print("User not found in database")
            raise credentials_exception

        # Debug role information
        print(f"User status: {user.status}")
        print(f"User role_id: {user.role_id}")
        print(f"User role object: {user.role}")
        if user.role:
            print(f"Role code: {user.role.code}")
            print(f"Role name: {user.role.name}")
        else:
            print("WARNING: User has no role assigned!")

        if user.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account status: {user.status}. Please contact administrator.",
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_current_user: {str(e)}")
        raise credentials_exception


# FIXED: Add /me endpoint that returns user with role information
@router.get("/me")
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    """Get current user information with role details"""

    # Return user info with role details
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "employee_code": current_user.employee_code,
        "department": current_user.department,
        "designation": current_user.designation,
        "status": current_user.status,
        "role_id": current_user.role_id,
        "role": None  # Default to None if no role
    }

    # Add role information if available
    if current_user.role:
        user_data["role"] = {
            "id": current_user.role.id,
            "name": current_user.role.name,
            "code": current_user.role.code,
            "description": current_user.role.description
        }

    return user_data


# Add this debug endpoint to test role loading
@router.get("/debug-user-role")
async def debug_user_role(
        current_user: User = Depends(get_current_user)
):
    """Debug endpoint to check user role loading"""

    return {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "user_status": current_user.status,
        "role_id": current_user.role_id,
        "role_exists": current_user.role is not None,
        "role_details": {
            "id": current_user.role.id if current_user.role else None,
            "name": current_user.role.name if current_user.role else None,
            "code": current_user.role.code if current_user.role else None,
            "description": current_user.role.description if current_user.role else None,
        } if current_user.role else None,
        "is_director": current_user.role and current_user.role.code == "DIRECTOR"
    }