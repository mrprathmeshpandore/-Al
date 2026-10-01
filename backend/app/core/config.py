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
    DB_POOL_SIZE: int = Field(default=10, description="PostgreSQL connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="PostgreSQL max overflow connections")
    DB_POOL_TIMEOUT: float = Field(default=30.0, description="PostgreSQL connection pool timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=1800, description="PostgreSQL connection pool recycle time in seconds")
    DB_POOL_PRE_PING: bool = Field(default=True, description="Enable connection pre-ping health check")

    # Redis Cache Configuration
    REDIS_URL: str = Field(default="", description="Redis URL (e.g. redis://localhost:6379/0)")
    CACHE_TTL_SECONDS: int = Field(default=300, description="Default cache TTL in seconds")

    # Storage Provider Configuration
    STORAGE_PROVIDER: str = Field(default="local", description="Storage provider (local, s3)")
    STORAGE_BUCKET: str = Field(default="", description="S3 bucket name")
    STORAGE_REGION: str = Field(default="us-east-1", description="S3 region")
    STORAGE_ENDPOINT: str = Field(default="", description="S3 endpoint URL")
    STORAGE_ACCESS_KEY: str = Field(default="", description="S3 access key")
    STORAGE_SECRET_KEY: str = Field(default="", description="S3 secret key")

    # API Keys & Secrets
    GEMINI_API_KEY: str = Field(default="", description="Gemini API Key for future RAG/AI modules")
    SECRET_KEY: str = Field(default="dev_secret_key_prashasak_ai_change_in_production_32bytes", description="Application secret key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 Hours

    # PDF & Resource Processing Pipeline Configuration
    MAX_PDF_SIZE_MB: int = Field(default=25, description="Maximum allowed PDF upload size in megabytes")
    STORAGE_DIR: str = Field(default="storage/resources", description="Directory path for resource file storage")
    CHUNK_SIZE: int = Field(default=1000, description="Target character length for document text chunks")
    CHUNK_OVERLAP: int = Field(default=150, description="Overlap character length between sequential chunks")

    # RAG & Vector Embedding Configuration
    GEMINI_EMBEDDING_MODEL: str = Field(default="text-embedding-004", description="Gemini embedding model name")
    GEMINI_GENERATION_MODEL: str = Field(default="gemini-1.5-flash", description="Gemini text generation model name")
    GEMINI_REQUEST_TIMEOUT: float = Field(default=30.0, description="Gemini API request timeout in seconds")
    GEMINI_MAX_RETRIES: int = Field(default=3, description="Maximum retries for Gemini API calls")
    GEMINI_MAX_TOKENS: int = Field(default=2048, description="Maximum output tokens for Gemini generation")
    EMBEDDING_DIMENSION: int = Field(default=768, description="Vector embedding float dimension")
    EMBEDDING_BATCH_SIZE: int = Field(default=16, description="Maximum batch size for chunk embedding API calls")
    RAG_TOP_K: int = Field(default=5, description="Default number of top relevant chunks to retrieve")
    RAG_MIN_SIMILARITY: float = Field(default=0.5, description="Minimum cosine similarity threshold for RAG retrieval")

    # Current Affairs Intelligence Engine Configuration
    CURRENT_AFFAIRS_ENABLED: bool = Field(default=True, description="Enable current affairs module")
    CURRENT_AFFAIRS_FETCH_LIMIT: int = Field(default=20, description="Max articles to fetch per source in batch")
    CURRENT_AFFAIRS_MAX_ARTICLE_LENGTH: int = Field(default=30000, description="Max article text character length")
    CURRENT_AFFAIRS_DEDUP_SIMILARITY: float = Field(default=0.90, description="Title similarity threshold for deduplication")
    CURRENT_AFFAIRS_ANALYSIS_ENABLED: bool = Field(default=True, description="Enable Gemini analysis during ingestion")
    CURRENT_AFFAIRS_DEFAULT_LOOKBACK_DAYS: int = Field(default=3, description="Default lookback window in days")

    # Voice Engine Configuration
    VOICE_STT_PROVIDER: str = Field(default="fake", description="Speech-to-Text provider (fake, google, whisper)")
    VOICE_TTS_PROVIDER: str = Field(default="fake", description="Text-to-Speech provider (fake, gtts, google)")
    VOICE_DEFAULT_LANGUAGE: str = Field(default="en-IN", description="Default voice language code")
    VOICE_DEFAULT_VOICE: str = Field(default="default", description="Default voice model/accent name")
    VOICE_MAX_AUDIO_SIZE_MB: int = Field(default=10, description="Maximum allowed audio upload size in MB")
    VOICE_MAX_DURATION_SECONDS: int = Field(default=180, description="Maximum allowed audio duration in seconds")

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:5173", "http://127.0.0.1:5173",
            "http://localhost:5174", "http://127.0.0.1:5174",
            "http://localhost:5175", "http://127.0.0.1:5175",
            "http://localhost:3000", "http://127.0.0.1:3000"
        ],
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

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        # Prevent completely empty secret key
        if not v or not v.strip():
            raise ValueError("SECRET_KEY must not be empty.")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def check_production_security(self) -> None:
        """Helper to enforce strict production security settings."""
        if self.ENVIRONMENT.lower() in ("production", "prod"):
            if "dev_secret" in self.SECRET_KEY.lower() or len(self.SECRET_KEY) < 32:
                raise ValueError("In production mode, SECRET_KEY must be a non-default string of at least 32 characters.")
            if "*" in self.CORS_ORIGINS or "http://*" in self.CORS_ORIGINS:
                raise ValueError("Wildcard '*' origins are not allowed in CORS_ORIGINS for production environment.")


settings = Settings()
