from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.profile import UserProfile
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Registers a new user account and initializes an empty UserProfile (DAF).
    """
    email_clean = payload.email.lower().strip()

    # 1. Check duplicate email
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address is already registered"
        )

    # 2. Hash password securely (Bcrypt)
    pwd_hash = hash_password(payload.password)

    # 3. Create User record
    user = User(
        email=email_clean,
        full_name=payload.full_name.strip(),
        password_hash=pwd_hash,
        is_active=True,
    )
    db.add(user)
    db.flush()  # Generate user.id

    # 4. Create default UserProfile linked to user
    profile = UserProfile(
        user_id=user.id,
        education_data={},
        upsc_journey_data={},
        interests={},
        perspective={},
        profile_completion=0,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticates user credentials and returns a JWT Bearer Token.
    """
    email_clean = payload.email.lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive account. Please contact administrator.",
        )

    access_token = create_access_token(subject=user.id, email=user.email)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Returns authenticated user account details using JWT Bearer authentication.
    """
    return current_user
