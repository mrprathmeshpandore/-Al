from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class PersonalInfoSchema(BaseModel):
    fullName: Optional[str] = None
    dob: Optional[str] = None
    homeState: Optional[str] = None
    district: Optional[str] = None
    currentCity: Optional[str] = None
    gender: Optional[str] = None
    photoUrl: Optional[str] = None


class EducationInfoSchema(BaseModel):
    degree: Optional[str] = None
    university: Optional[str] = None
    specialization: Optional[str] = None
    postGraduation: Optional[str] = None
    otherQualifications: Optional[str] = None


class UPSCJourneyInfoSchema(BaseModel):
    attemptCount: Optional[str] = None
    optionalSubject: Optional[str] = None
    previousInterviewExp: Optional[str] = None
    preparationStage: Optional[str] = None


class InterestsInfoSchema(BaseModel):
    hobbies: Optional[str] = None
    sports: Optional[str] = None
    readingBooks: Optional[str] = None
    areasOfInterest: Optional[str] = None
    socialActivities: Optional[str] = None


class PerspectiveInfoSchema(BaseModel):
    whyCivilServices: Optional[str] = None
    keyFocusAreas: Optional[str] = None
    boardMessage: Optional[str] = None


class UserProfileUpdatePayload(BaseModel):
    personal: Optional[Dict[str, Any]] = None
    education: Optional[Dict[str, Any]] = None
    upscJourney: Optional[Dict[str, Any]] = None
    interests: Optional[Dict[str, Any]] = None
    perspective: Optional[Dict[str, Any]] = None


class UserProfileData(BaseModel):
    id: str
    user_id: str
    personal: Dict[str, Any]
    education: Dict[str, Any]
    upscJourney: Dict[str, Any]
    interests: Dict[str, Any]
    perspective: Dict[str, Any]
    profile_completion: int = Field(default=0, ge=0, le=100)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    profile: UserProfileData
    completion_percentage: int
