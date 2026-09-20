from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.profile import UserProfile
from app.schemas.profile import ProfileResponse, UserProfileUpdatePayload, UserProfileData

router = APIRouter(prefix="/profile", tags=["User Profile & DAF"])


def calculate_completion_percentage(profile: UserProfile, user_full_name: str) -> int:
    """
    Calculates backend profile completion percentage (0-100%) based on completed DAF fields across 5 sections.
    """
    completed_steps = 0

    # Step 1: Personal
    p_dob = profile.date_of_birth or ""
    p_state = profile.home_state or ""
    p_dist = profile.district or ""
    p_city = profile.current_city or ""
    p_gender = profile.gender or ""
    if user_full_name and p_dob and p_state and p_dist and p_city and p_gender:
        completed_steps += 1

    # Step 2: Education
    edu = profile.education_data or {}
    degree = edu.get("degree") or ""
    uni = edu.get("university") or ""
    spec = edu.get("specialization") or ""
    if degree and uni and spec:
        completed_steps += 1

    # Step 3: UPSC Journey
    uj = profile.upsc_journey_data or {}
    att_cnt = uj.get("attemptCount") or ""
    opt_sub = uj.get("optionalSubject") or ""
    prep_stg = uj.get("preparationStage") or ""
    if att_cnt and opt_sub and prep_stg:
        completed_steps += 1

    # Step 4: Interests
    intr = profile.interests or {}
    hobbies = intr.get("hobbies") or ""
    if hobbies:
        completed_steps += 1

    # Step 5: Perspective
    persp = profile.perspective or {}
    why_cs = persp.get("whyCivilServices") or ""
    focus = persp.get("keyFocusAreas") or ""
    if why_cs or focus:
        completed_steps += 1

    return completed_steps * 20


def format_profile_response(profile: UserProfile, user: User) -> ProfileResponse:
    completion_pct = calculate_completion_percentage(profile, user.full_name)
    profile.profile_completion = completion_pct

    edu = profile.education_data or {}
    uj = profile.upsc_journey_data or {}
    intr = profile.interests or {}
    persp = profile.perspective or {}

    personal_data = {
        "fullName": user.full_name,
        "dob": profile.date_of_birth or "",
        "homeState": profile.home_state or "",
        "district": profile.district or "",
        "currentCity": profile.current_city or "",
        "gender": profile.gender or "",
        "photoUrl": None,
    }

    profile_data = UserProfileData(
        id=profile.id,
        user_id=profile.user_id,
        personal=personal_data,
        education=edu,
        upscJourney=uj,
        interests=intr,
        perspective=persp,
        profile_completion=completion_pct,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )

    return ProfileResponse(
        profile=profile_data,
        completion_percentage=completion_pct,
    )


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gets the current authenticated user's DAF Profile data and calculated completion percentage.
    """
    profile = current_user.profile
    if not profile:
        profile = UserProfile(
            user_id=current_user.id,
            education_data={},
            upsc_journey_data={},
            interests={},
            perspective={},
            profile_completion=0,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return format_profile_response(profile, current_user)


@router.put("", response_model=ProfileResponse)
def update_profile(
    payload: UserProfileUpdatePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates the authenticated user's DAF Profile data and recalculates completion percentage.
    """
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # 1. Update Personal Info & User full_name
    if payload.personal:
        p = payload.personal
        if "fullName" in p and p["fullName"]:
            current_user.full_name = p["fullName"].strip()
        if "dob" in p:
            profile.date_of_birth = p["dob"]
        if "homeState" in p:
            profile.home_state = p["homeState"]
        if "district" in p:
            profile.district = p["district"]
        if "currentCity" in p:
            profile.current_city = p["currentCity"]
        if "gender" in p:
            profile.gender = p["gender"]

    # 2. Update Education Info
    if payload.education is not None:
        profile.education_data = payload.education

    # 3. Update UPSC Journey Info
    if payload.upscJourney is not None:
        profile.upsc_journey_data = payload.upscJourney

    # 4. Update Interests Info
    if payload.interests is not None:
        profile.interests = payload.interests

    # 5. Update Perspective Info
    if payload.perspective is not None:
        profile.perspective = payload.perspective

    profile.updated_at = datetime.now(timezone.utc)
    current_user.updated_at = datetime.now(timezone.utc)

    # Recalculate completion
    completion_pct = calculate_completion_percentage(profile, current_user.full_name)
    profile.profile_completion = completion_pct

    db.commit()
    db.refresh(profile)
    db.refresh(current_user)

    return format_profile_response(profile, current_user)
