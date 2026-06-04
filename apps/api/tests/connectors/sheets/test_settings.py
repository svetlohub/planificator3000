from app.config import Settings


def test_google_sheets_settings_can_be_loaded_from_environment(monkeypatch) -> None:
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
