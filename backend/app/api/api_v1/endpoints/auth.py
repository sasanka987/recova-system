from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
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

    # TODO: Send notification to directors about new registration

    return db_user


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """Login user and return access token"""

    # Find user by email
    user = db.query(User).filter(User.email == form_data.username).first()

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


# Replace the get_current_user function in your auth.py file

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""

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

        user = db.query(User).filter(User.email == email).first()
        print(f"User found: {user is not None}")

        if user is None:
            print("User not found in database")
            raise credentials_exception

        print(f"User status: {user.status}")
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


# Add this debug endpoint to auth.py to isolate the issue

@router.post("/debug-login")
async def debug_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """Debug version of login to identify the issue"""

    try:
        print(f"Attempting login for: {form_data.username}")

        # Test database connection
        user_count = db.query(User).count()
        print(f"Total users in database: {user_count}")

        # Find user by email
        user = db.query(User).filter(User.email == form_data.username).first()
        print(f"User found: {user is not None}")

        if not user:
            return {"error": "User not found", "username": form_data.username}

        print(f"User status: {user.status}")
        print(f"User role_id: {user.role_id}")

        # Test password verification
        from app.core.security import verify_password
        password_valid = verify_password(form_data.password, user.password_hash)
        print(f"Password valid: {password_valid}")

        if not password_valid:
            return {"error": "Invalid password"}

        # Test token creation
        from app.core.security import create_access_token
        from datetime import timedelta
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            subject=user.email, expires_delta=access_token_expires
        )
        print(f"Token created successfully: {len(access_token)} characters")

        return {
            "success": True,
            "user_id": user.id,
            "user_email": user.email,
            "user_status": user.status,
            "token_length": len(access_token)
        }

    except Exception as e:
        print(f"Error in debug login: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "error_type": type(e).__name__}