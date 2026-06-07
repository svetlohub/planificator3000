"""
Tests for GET /api/v1/plans/current.

Strategy: inject a fake SheetsRepository via app.state so no real
Google credentials are required.  Row dicts use the column alias names
that SheetsRepository._load_rows passes into the DTO constructors.
"""
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.connectors.sheets import SheetsRepository
from app.main import create_app

# ─────────────────────────────────────────── fake client & helpers


class _FakeClient:
    """Minimal protocol-compatible client returning caller-supplied rows per worksheet."""

    def __init__(self, data: dict[str, list[dict]]) -> None:
        self._data = data

    def read_records(self, worksheet_name: str) -> list[dict]:
        return self._data.get(worksheet_name, [])

    def health_check(self) -> bool:
        return True


_SETTINGS = Settings(
    app_env="local",
    google_sheet_id="sheet-test",
    google_service_account_json='{"type":"service_account"}',
)

# Minimal valid rows using sheet column alias names
_TASK_ROW = {
    "Task ID": "T-001",
    "Title": "Тестовая задача",
    "Status": "planned",
    "Owner": "Алиса",
    "Assignee": "",
    "Estimate Hours": "2",
    "Task Type": "analysis",
    "Week": "2025-W20",
}

_COMPLETED_ROW = {
    "Task ID": "T-002",
    "Title": "Закрыть баг",
    "Owner": "Борис",
    "Assignee": "",
    "Estimate Hours": "1",
    "Task Type": "routine",
    "Week": "2025-W19",
}

_RECURRING_ROW = {
    "Task ID": "T-003",
    "Title": "Стендап",
    "Owner": "Алиса",
    "Assignee": "",
    "Estimate Hours": "0.25",
    "Task Type": "meeting",
    "Week": "2025-W20",
}

_TEAM_ROW = {
    "Name": "Алиса Иванова",
    "Weekly Capacity Hours": "40",
    "Reserved Buffer Percent": "20",
    "Skills": "python, design",
}


def _make_test_client(
    monthly_rows: list[dict] | None = None,
    completed_rows: list[dict] | None = None,
    recurring_rows: list[dict] | None = None,
    team_rows: list[dict] | None = None,
) -> TestClient:
    data = {
        _SETTINGS.google_worksheet_monthly_plan: monthly_rows or [],
        _SETTINGS.google_worksheet_completed_tasks: completed_rows or [],
        _SETTINGS.google_worksheet_recurring_tasks: recurring_rows or [],
        _SETTINGS.google_worksheet_team_roster: team_rows or [],
        _SETTINGS.google_worksheet_config: [],
    }
    repo = SheetsRepository(client=_FakeClient(data), settings=_SETTINGS)

    app = create_app()
    app.state.sheets_repository = repo
    return TestClient(app)


# ─────────────────────────────────────────── response shape


def test_current_plan_returns_200() -> None:
    client = _make_test_client()
    assert client.get("/api/v1/plans/current").status_code == 200


def test_current_plan_response_has_required_keys() -> None:
    body = _make_test_client().get("/api/v1/plans/current").json()
    assert "tasks" in body
    assert "team" in body
    assert "sheets_configured" in body


def test_current_plan_sheets_configured_true() -> None:
    body = _make_test_client().get("/api/v1/plans/current").json()
    assert body["sheets_configured"] is True


# ─────────────────────────────────────────── empty sheets


def test_empty_sheets_return_empty_lists() -> None:
    body = _make_test_client().get("/api/v1/plans/current").json()
    assert body["tasks"] == []
    assert body["team"] == []


# ─────────────────────────────────────────── team members


def test_team_member_returned() -> None:
    body = _make_test_client(team_rows=[_TEAM_ROW]).get("/api/v1/plans/current").json()
    assert len(body["team"]) == 1
    assert body["team"][0]["name"] == "Алиса Иванова"


def test_team_member_available_capacity_hours_computed() -> None:
    # 40h * (1 - 0.20) = 32h
    body = _make_test_client(team_rows=[_TEAM_ROW]).get("/api/v1/plans/current").json()
    assert float(body["team"][0]["available_capacity_hours"]) == pytest.approx(32.0)


def test_multiple_team_members_returned() -> None:
    second = {**_TEAM_ROW, "Name": "Борис Смирнов"}
    body = _make_test_client(team_rows=[_TEAM_ROW, second]).get("/api/v1/plans/current").json()
    assert len(body["team"]) == 2


# ─────────────────────────────────────────── tasks per source


def test_monthly_plan_task_included() -> None:
    body = _make_test_client(monthly_rows=[_TASK_ROW]).get("/api/v1/plans/current").json()
    assert len(body["tasks"]) == 1
    assert body["tasks"][0]["title"] == "Тестовая задача"
    assert body["tasks"][0]["source"] == "monthly_plan"


def test_completed_task_included() -> None:
    body = _make_test_client(completed_rows=[_COMPLETED_ROW]).get("/api/v1/plans/current").json()
    assert len(body["tasks"]) == 1
    assert body["tasks"][0]["status"] == "done"
    assert body["tasks"][0]["source"] == "completed_tasks"


def test_recurring_task_included() -> None:
    body = _make_test_client(recurring_rows=[_RECURRING_ROW]).get("/api/v1/plans/current").json()
    assert len(body["tasks"]) == 1
    assert body["tasks"][0]["source"] == "recurring_tasks"


def test_all_three_sources_aggregated() -> None:
    body = _make_test_client(
        monthly_rows=[_TASK_ROW],
        completed_rows=[_COMPLETED_ROW],
        recurring_rows=[_RECURRING_ROW],
    ).get("/api/v1/plans/current").json()
    assert len(body["tasks"]) == 3


# ─────────────────────────────────────────── no repository → 503


def test_returns_503_when_no_repository_configured() -> None:
    app = create_app()
    app.state.sheets_repository = None
    client = TestClient(app, raise_server_exceptions=False)
    assert client.get("/api/v1/plans/current").status_code == 503
