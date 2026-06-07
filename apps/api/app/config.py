from functools import lru_cache
from typing import Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ПЛАНИФИКАТОР-3000 API"
    app_env: str = "local"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    google_sheet_id: str | None = None
    google_service_account_json: str | None = None
    google_worksheet_completed_tasks: str = "Completed Tasks"
    google_worksheet_monthly_plan: str = "Monthly Plan"
    google_worksheet_recurring_tasks: str = "Recurring Tasks"
    google_worksheet_team_roster: str = "Team Roster"
    google_worksheet_config: str = "Config"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def require_google_credentials_outside_local(self) -> Self:
        if self.app_env != "local":
            missing: list[str] = []
            if not self.google_sheet_id:
                missing.append("GOOGLE_SHEET_ID")
            if not self.google_service_account_json:
                missing.append("GOOGLE_SERVICE_ACCOUNT_JSON")
            if missing:
                msg = (
                    f"Required environment variables are not set for app_env={self.app_env!r}: "
                    f"{', '.join(missing)}"
                )
                raise ValueError(msg)
        return self

    @property
    def sheets_configured(self) -> bool:
        """True when both Google Sheets credentials are present."""
        return bool(self.google_sheet_id and self.google_service_account_json)


@lru_cache
def get_settings() -> Settings:
    return Settings()
