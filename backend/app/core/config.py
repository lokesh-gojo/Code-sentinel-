from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application Settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    ENVIRONMENT: str = Field(default="development")
    PORT: int = Field(default=8000)
    HOST: str = Field(default="0.0.0.0")
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:3000,https://*.vercel.app")

    # Supabase Configuration
    SUPABASE_URL: str = Field(default="https://mock.supabase.co")
    SUPABASE_KEY: str = Field(default="mock-key")
    SUPABASE_JWT_SECRET: str = Field(default="mock-jwt-secret")

    # Gemini LLM
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash")

    # E2B Sandbox
    E2B_API_KEY: str = Field(default="")

    # GitHub App / Token
    GITHUB_TOKEN: str = Field(default="")

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
