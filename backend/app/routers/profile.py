import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.profile import UserProfile
from app.schemas.profile import UserProfileResponse, UserProfileUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["User Profile"])


@router.get("/{user_id}", response_model=UserProfileResponse, summary="Get User Profile")
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Fetches the DAF profile for a specified user ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"User profile lookup failed: User '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        logger.warning(f"Profile lookup failed: UserProfile for user '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return profile


@router.put("/{user_id}", response_model=UserProfileResponse, summary="Update User Profile")
def update_user_profile(
    user_id: str,
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates the DAF profile for a specified user ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Profile update failed: User '{user_id}' not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        # Create profile if not present
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    update_dict = profile_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(profile, key, value)

    profile.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(profile)
        logger.info(f"Successfully updated UserProfile for user '{user_id}'.")
        return profile
    except Exception as e:
        db.rollback()
        logger.error(f"Database error while updating profile for user '{user_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
