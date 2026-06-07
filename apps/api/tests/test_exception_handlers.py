"""
Tests for registered SheetsError exception handlers.

Strategy: mount a tiny test router that raises specific exceptions,
then verify that create_app() converts them to the correct HTTP responses
without leaking Python tracebacks.
"""
from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.connectors.sheets.exceptions import (
    InvalidSheetDataError,
    SheetAccessError,
    SheetsError,
    WorksheetNotFoundError,
)
from app.main import create_app


def _app_with_error_routes() -> TestClient:
    """Return a TestClient for an app with four error-trigger routes."""
    app = create_app()

    probe = APIRouter(prefix="/probe")

    @probe.get("/sheets-error")
    def raise_sheets_error() -> None:
        raise SheetsError("base sheets failure")

    @probe.get("/sheet-access")
    def raise_sheet_access() -> None:
        raise SheetAccessError("spreadsheet unreachable")

    @probe.get("/worksheet-not-found")
    def raise_worksheet_not_found() -> None:
        raise WorksheetNotFoundError("Recurring Tasks not found")

    @probe.get("/invalid-data")
    def raise_invalid_data() -> None:
        raise InvalidSheetDataError("row 7 malformed")

    app.include_router(probe)
    return TestClient(app, raise_server_exceptions=False)


client = _app_with_error_routes()


def test_sheets_error_returns_503() -> None:
    response = client.get("/probe/sheets-error")

    assert response.status_code == 503
    body = response.json()
    assert body["detail"] == "Google Sheets service unavailable"
    assert "base sheets failure" in body["error"]


def test_sheet_access_error_returns_503() -> None:
    response = client.get("/probe/sheet-access")

    assert response.status_code == 503
    body = response.json()
    assert body["detail"] == "Cannot access Google Sheets"
    assert "spreadsheet unreachable" in body["error"]


def test_worksheet_not_found_returns_503() -> None:
    response = client.get("/probe/worksheet-not-found")

    assert response.status_code == 503
    body = response.json()
    assert body["detail"] == "Configured worksheet not found"
    assert "Recurring Tasks not found" in body["error"]


def test_invalid_sheet_data_returns_422() -> None:
    response = client.get("/probe/invalid-data")

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Invalid data in Google Sheets"
    assert "row 7 malformed" in body["error"]


def test_exception_response_has_no_traceback() -> None:
    """Response body must never contain a Python traceback."""
    response = client.get("/probe/sheets-error")

    raw = response.text
    assert "Traceback" not in raw
    assert "File " not in raw
