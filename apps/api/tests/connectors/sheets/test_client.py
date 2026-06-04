from typing import Any

import pytest
from app.connectors.sheets.client import GoogleSheetsClient, WorksheetProtocol
from app.connectors.sheets.exceptions import SheetAccessError


class FakeWorksheet:
    title = "Fake"

    def __init__(self) -> None:
        self.cleared = False
        self.updated_values: list[list[object]] | None = None

    def get_all_records(self) -> list[dict[str, Any]]:
        return [{"A": 1}]

    def clear(self) -> None:
        self.cleared = True

    def update(self, values, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
        self.updated_values = values


class TestableGoogleSheetsClient(GoogleSheetsClient):
    def __init__(self, worksheet: FakeWorksheet) -> None:
        super().__init__(sheet_id="sheet-id", service_account_json="{}")
        self.worksheet = worksheet

    def get_worksheet(self, worksheet_name: str) -> WorksheetProtocol:
        return self.worksheet


def test_read_records_uses_worksheet_records() -> None:
    client = TestableGoogleSheetsClient(FakeWorksheet())

    assert client.read_records("Any") == [{"A": 1}]


def test_write_records_writes_header_and_rows() -> None:
    worksheet = FakeWorksheet()
    client = TestableGoogleSheetsClient(worksheet)

    client.write_records("Any", [{"A": 1, "B": "x"}])

    assert worksheet.cleared is True
    assert worksheet.updated_values == [["A", "B"], [1, "x"]]


def test_write_records_rejects_inconsistent_keys() -> None:
    client = TestableGoogleSheetsClient(FakeWorksheet())

    with pytest.raises(SheetAccessError, match="same keys"):
        client.write_records("Any", [{"A": 1}, {"B": 2}])


def test_clear_worksheet_clears_worksheet() -> None:
    worksheet = FakeWorksheet()
    client = TestableGoogleSheetsClient(worksheet)

    client.clear_worksheet("Any")

    assert worksheet.cleared is True
