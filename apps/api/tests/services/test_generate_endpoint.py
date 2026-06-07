"""
Integration test for GET /api/v1/plans/generate.

Uses a fake SheetsRepository injected via app.state — no real Google API.
Verifies that the full pipeline (Sheets → Mapper → Orchestrator → Response)
produces a valid WeeklyPlanResult JSON response.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.connectors.sheets import SheetsRepository
from app.main import create_app

WEEK = "2026-W25"

# ─────────────────────────────── fake infrastructure


class _FakeClient:
    def __init__(self, data: dict[str, list[dict[str, Any]]]) -> None:
        self._data = data

    def read_records(self, worksheet_name: str) -> list[dict[str, Any]]:
        return self._data.get(worksheet_name, [])

    def health_check(self) -> bool:
        return True


_SETTINGS = Settings(
    app_env="local",
    google_sheet_id="sheet-test",
    google_service_account_json='{"type":"service_account"}',
)

_TEAM_ROW = {
    "Name": "Алиса",
    "Weekly Capacity Hours": "40",
    "Reserved Buffer Percent": "25",
    "Skills": "python",
}

_MONTHLY_ROW = {
    "Task ID": "M-001",
    "Title": "Написать спеку",
    "Status": "planned",
    "Owner": "Алиса",
    "Assignee": "",
    "Estimate Hours": "2",
    "Task Type": "analysis",
    "Week": WEEK,
}

_RECURRING_ROW = {
    "Task ID": "R-001",
    "Title": "Стендап",
    "Owner": "Алиса",
    "Assignee": "",
    "Estimate Hours": "0.25",
    "Task Type": "meeting",
    "Week": WEEK,
}


def _make_client(
    team_rows: list[dict] | None = None,
    monthly_rows: list[dict] | None = None,
    recurring_rows: list[dict] | None = None,
    completed_rows: list[dict] | None = None,
    config_rows: list[dict] | None = None,
) -> TestClient:
    data = {
        _SETTINGS.google_worksheet_team_roster: team_rows or [],
        _SETTINGS.google_worksheet_monthly_plan: monthly_rows or [],
        _SETTINGS.google_worksheet_recurring_tasks: recurring_rows or [],
        _SETTINGS.google_worksheet_completed_tasks: completed_rows or [],
        _SETTINGS.google_worksheet_config: config_rows or [],
    }
    repo = SheetsRepository(client=_FakeClient(data), settings=_SETTINGS)
    app = create_app()
    app.state.sheets_repository = repo
    return TestClient(app)


# ─────────────────────────────── response shape


def test_generate_returns_200() -> None:
    client = _make_client()
    response = client.get(f"/api/v1/plans/generate?week_ref={WEEK}")
    assert response.status_code == 200


def test_generate_response_has_required_keys() -> None:
    body = _make_client().get(f"/api/v1/plans/generate?week_ref={WEEK}").json()

    for key in (
        "week_ref",
        "scheduled_tasks",
        "backlog_tasks",
        "allocations",
        "team_capacity",
        "total_capacity_hours",
        "planned_hours",
        "backlog_hours",
    ):
        assert key in body, f"Missing key: {key}"


def test_generate_week_ref_in_response() -> None:
    body = _make_client().get(f"/api/v1/plans/generate?week_ref={WEEK}").json()
    assert body["week_ref"] == WEEK


# ─────────────────────────────── empty scenario


def test_generate_empty_sheets_returns_zero_hours() -> None:
    body = _make_client().get(f"/api/v1/plans/generate?week_ref={WEEK}").json()

    assert body["scheduled_tasks"] == []
    assert body["backlog_tasks"] == []
    assert body["total_capacity_hours"] == 0.0
    assert body["planned_hours"] == 0.0


# ─────────────────────────────── task scheduling


def test_generate_schedules_monthly_task() -> None:
    client = _make_client(
        team_rows=[_TEAM_ROW],
        monthly_rows=[_MONTHLY_ROW],
    )
    body = client.get(f"/api/v1/plans/generate?week_ref={WEEK}").json()

    assert len(body["scheduled_tasks"]) == 1
    assert body["scheduled_tasks"][0]["task_id"] == "M-001"


def test_generate_schedules_recurring_task() -> None:
    client = _make_client(
        team_rows=[_TEAM_ROW],
        recurring_rows=[_RECURRING_ROW],
    )
    body = client.get(f"/api/v1/plans/generate?week_ref={WEEK}").json()

    assert len(body["scheduled_tasks"]) == 1
    assert body["scheduled_tasks"][0]["task_id"] == "R-001"


def test_generate_capacity_in_result() -> None:
    client = _make_client(team_rows=[_TEAM_ROW])
    body = client.get(f"/api/v1/plans/generate?week_ref={WEEK}").json()

    assert len(body["team_capacity"]) == 1
    # 40h * 0.75 = 30h
    assert body["total_capacity_hours"] == pytest.approx(30.0)


# ─────────────────────────────── 503 without repository


def test_generate_returns_503_without_repository() -> None:
    app = create_app()
    app.state.sheets_repository = None
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get(f"/api/v1/plans/generate?week_ref={WEEK}")
    assert response.status_code == 503


# ─────────────────────────────── config integration


def test_generate_uses_config_buffer_percent() -> None:
    member_no_override = {**_TEAM_ROW, "Reserved Buffer Percent": "0"}  # use global
    config = [{"Key": "buffer_percent", "Value": "20"}]

    client = _make_client(team_rows=[member_no_override], config_rows=config)
    body = client.get(f"/api/v1/plans/generate?week_ref={WEEK}").json()

    # 40 * 0.80 = 32h
    assert body["total_capacity_hours"] == pytest.approx(32.0)
