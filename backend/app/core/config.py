import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Prashasak AI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Environment
    ENVIRONMENT: str = "development"

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./prashasak_ai_dev.db",
        description="PostgreSQL Database connection URL"
    )

    # API Keys & Secrets
    GEMINI_API_KEY: str = Field(default="", description="Gemini API Key for future RAG/AI modules")
    SECRET_KEY: str = Field(default="dev_secret_key_prashasak_ai_change_in_production_32bytes", description="Application secret key")

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
