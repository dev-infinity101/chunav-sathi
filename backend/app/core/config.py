from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_id: str = Field(default="", alias="PROJECT_ID")
    region: str = Field(default="asia-south1", alias="REGION")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    # Comma-separated; in production this is left empty (same-origin)
    allowed_origins: str = Field(
        default="http://localhost:5173", alias="ALLOWED_ORIGINS"
    )
    env: str = Field(default="development", alias="ENV")

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()
