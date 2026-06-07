import pytest
from pydantic import ValidationError

from app.config import Settings


# ------------------------------------------------------------------ local env


def test_local_env_starts_without_google_credentials() -> None:
    """app_env=local must not require Google credentials."""
    settings = Settings(app_env="local")

    assert settings.google_sheet_id is None
    assert settings.google_service_account_json is None
    assert settings.sheets_configured is False


def test_sheets_configured_true_when_both_credentials_present() -> None:
    settings = Settings(
        app_env="local",
        google_sheet_id="sheet-abc",
        google_service_account_json='{"type":"service_account"}',
    )

    assert settings.sheets_configured is True


def test_sheets_configured_false_when_sheet_id_missing() -> None:
    settings = Settings(
        app_env="local",
        google_sheet_id=None,
        google_service_account_json='{"type":"service_account"}',
    )

    assert settings.sheets_configured is False


def test_sheets_configured_false_when_service_account_missing() -> None:
    settings = Settings(
        app_env="local",
        google_sheet_id="sheet-abc",
        google_service_account_json=None,
    )

    assert settings.sheets_configured is False


# ------------------------------------------------------- non-local env guard


def test_staging_env_raises_when_sheet_id_missing() -> None:
    with pytest.raises(ValidationError, match="GOOGLE_SHEET_ID"):
        Settings(
            app_env="staging",
            google_sheet_id=None,
            google_service_account_json='{"type":"service_account"}',
        )


def test_staging_env_raises_when_service_account_missing() -> None:
    with pytest.raises(ValidationError, match="GOOGLE_SERVICE_ACCOUNT_JSON"):
        Settings(
            app_env="staging",
            google_sheet_id="sheet-abc",
            google_service_account_json=None,
        )


def test_staging_env_raises_listing_all_missing_credentials() -> None:
    with pytest.raises(ValidationError, match="GOOGLE_SHEET_ID"):
        Settings(app_env="staging")


def test_production_env_raises_when_credentials_missing() -> None:
    with pytest.raises(ValidationError, match="GOOGLE_SERVICE_ACCOUNT_JSON"):
        Settings(app_env="production", google_sheet_id="sheet-abc")


def test_staging_env_starts_when_credentials_present() -> None:
    settings = Settings(
        app_env="staging",
        google_sheet_id="sheet-abc",
        google_service_account_json='{"type":"service_account"}',
    )

    assert settings.sheets_configured is True


# ------------------------------------------------------- cors origin parsing


def test_cors_origins_parsed_from_comma_separated_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, https://app.example.com")

    settings = Settings()

    assert settings.cors_origins == ["http://localhost:3000", "https://app.example.com"]


def test_cors_origins_accepts_list_directly() -> None:
    settings = Settings(cors_origins=["http://localhost:3000"])

    assert settings.cors_origins == ["http://localhost:3000"]


# ------------------------------------------------------- existing test compat


def test_google_sheets_settings_can_be_loaded_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-123")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
    monkeypatch.setenv("GOOGLE_WORKSHEET_COMPLETED_TASKS", "Done")
    monkeypatch.setenv("GOOGLE_WORKSHEET_MONTHLY_PLAN", "Monthly")
    monkeypatch.setenv("GOOGLE_WORKSHEET_RECURRING_TASKS", "Recurring")
    monkeypatch.setenv("GOOGLE_WORKSHEET_TEAM_ROSTER", "Roster")
    monkeypatch.setenv("GOOGLE_WORKSHEET_CONFIG", "Settings")

    settings = Settings()

    assert settings.google_sheet_id == "sheet-123"
    assert settings.google_service_account_json == '{"type":"service_account"}'
    assert settings.google_worksheet_completed_tasks == "Done"
    assert settings.google_worksheet_monthly_plan == "Monthly"
    assert settings.google_worksheet_recurring_tasks == "Recurring"
    assert settings.google_worksheet_team_roster == "Roster"
    assert settings.google_worksheet_config == "Settings"
