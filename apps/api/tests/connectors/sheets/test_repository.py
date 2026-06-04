from typing import Any

import pytest
from app.config import Settings
from app.connectors.sheets import InvalidSheetDataError, SheetsRepository


class FakeSheetsClient:
    def __init__(self, records_by_worksheet: dict[str, list[dict[str, Any]]]) -> None:
        self.records_by_worksheet = records_by_worksheet
        self.read_calls: list[str] = []

    def read_records(self, worksheet_name: str) -> list[dict[str, Any]]:
        self.read_calls.append(worksheet_name)
        return self.records_by_worksheet[worksheet_name]

    def health_check(self) -> bool:
        return True


def test_repository_loads_completed_tasks_as_dto() -> None:
    client = FakeSheetsClient(
        {
            "Done": [
                {
                    "Task ID": "done-1",
                    "Title": "Close weekly report",
                    "Owner": "Irina",
                    "Assignee": "Alex",
                    "Estimate Hours": 2,
                    "Task Type": "reporting",
                    "Week": "2026-W23",
                },
            ],
        },
    )
    settings = Settings(google_worksheet_completed_tasks="Done")
    repository = SheetsRepository(client, settings)

    rows = repository.load_completed_tasks()

    assert client.read_calls == ["Done"]
    assert rows[0].task_id == "done-1"


def test_repository_loads_config_as_dto() -> None:
    client = FakeSheetsClient({"Config": [{"Key": "timezone", "Value": "UTC"}]})
    repository = SheetsRepository(client, Settings())

    rows = repository.load_config()

    assert rows[0].key == "timezone"
    assert rows[0].value == "UTC"


def test_repository_wraps_invalid_sheet_rows() -> None:
    client = FakeSheetsClient({"Monthly Plan": [{"Task ID": "missing-required-fields"}]})
    repository = SheetsRepository(client, Settings())

    with pytest.raises(InvalidSheetDataError, match="Monthly Plan"):
        repository.load_monthly_plan()


def test_repository_exposes_client_health_check() -> None:
    client = FakeSheetsClient({})
    repository = SheetsRepository(client, Settings())

    assert repository.health_check() is True
