from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import uuid
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.profile import UserProfile
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    GoogleLoginRequest,
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


@router.post("/google", response_model=TokenResponse)
def google_login(
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticates user using Google OAuth ID Token credential.
    Automatically provisions account & UserProfile for new Google users.
    Returns JWT Bearer Token.
    """
    token_str = payload.credential.strip()
    google_data = None

    # 1. Try verifying via official google-auth library
    try:
        client_id = settings.GOOGLE_CLIENT_ID or None
        google_data = id_token.verify_oauth2_token(
            token_str,
            google_requests.Request(),
            audience=client_id,
        )
    except Exception:
        # Fallback to Google tokeninfo API endpoint verification
        try:
            resp = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token_str}", timeout=10)
            if resp.status_code == 200:
                google_data = resp.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired Google OAuth credential token."
                )
        except HTTPException:
            raise
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Google authentication failed: {err}"
            )

    if not google_data or not google_data.get("email"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account did not return a valid email address."
        )

    email = google_data["email"].lower().strip()
    full_name = google_data.get("name") or google_data.get("given_name") or email.split("@")[0]
    google_id = google_data.get("sub") or google_data.get("user_id")

    # 2. Query existing user by google_id or email
    user = db.query(User).filter((User.google_id == google_id) | (User.email == email)).first()

    if not user:
        random_pwd = hash_password(str(uuid.uuid4()))
        user = User(
            email=email,
            full_name=full_name.strip(),
            password_hash=random_pwd,
            google_id=google_id,
            is_active=True,
        )
        db.add(user)
        db.flush()

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
    else:
        if not user.google_id and google_id:
            user.google_id = google_id
            db.commit()
            db.refresh(user)

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
