from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field


class UserProfileBase(BaseModel):
    date_of_birth: Optional[str] = None
    home_state: Optional[str] = None
    district: Optional[str] = None
    current_city: Optional[str] = None
    gender: Optional[str] = None
    education_data: Optional[Dict[str, Any]] = None
    upsc_journey_data: Optional[Dict[str, Any]] = None
    interests: Optional[Dict[str, Any]] = None
    perspective: Optional[Dict[str, Any]] = None
    profile_completion: Optional[int] = Field(default=0, ge=0, le=100)


class UserProfileCreate(UserProfileBase):
    user_id: str


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
