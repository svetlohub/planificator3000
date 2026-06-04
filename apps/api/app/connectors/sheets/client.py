from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Protocol, cast

import gspread
from google.oauth2 import service_account
from gspread.exceptions import APIError, SpreadsheetNotFound, WorksheetNotFound

from app.connectors.sheets.exceptions import SheetAccessError, SheetsError, WorksheetNotFoundError

SCOPES = ("https://www.googleapis.com/auth/spreadsheets",)


class WorksheetProtocol(Protocol):
    title: str

    def get_all_records(self) -> list[dict[str, Any]]: ...

    def clear(self) -> None: ...

    def update(self, values: Sequence[Sequence[object]], *args: Any, **kwargs: Any) -> Any: ...


class SpreadsheetProtocol(Protocol):
    title: str

    def worksheet(self, title: str) -> WorksheetProtocol: ...


class GSpreadClientProtocol(Protocol):
    def open_by_key(self, key: str) -> SpreadsheetProtocol: ...


class GoogleSheetsClient:
    """Small gspread wrapper used by repositories, not by domain services."""

    def __init__(self, sheet_id: str, service_account_json: str) -> None:
        self._sheet_id = sheet_id
        self._service_account_json = service_account_json
        self._gspread_client: GSpreadClientProtocol | None = None
        self._spreadsheet: SpreadsheetProtocol | None = None

    def get_worksheet(self, worksheet_name: str) -> WorksheetProtocol:
        try:
            return self._get_spreadsheet().worksheet(worksheet_name)
        except WorksheetNotFound as exc:
            msg = f"Worksheet not found: {worksheet_name}"
            raise WorksheetNotFoundError(msg) from exc
        except APIError as exc:
            msg = f"Google Sheets API error while accessing worksheet: {worksheet_name}"
            raise SheetAccessError(msg) from exc

    def read_records(self, worksheet_name: str) -> list[dict[str, Any]]:
        try:
            return self.get_worksheet(worksheet_name).get_all_records()
        except SheetsError:
            raise
        except APIError as exc:
            msg = f"Google Sheets API error while reading worksheet: {worksheet_name}"
            raise SheetAccessError(msg) from exc

    def write_records(self, worksheet_name: str, records: Sequence[Mapping[str, object]]) -> None:
        worksheet = self.get_worksheet(worksheet_name)
        if not records:
            self.clear_worksheet(worksheet_name)
            return

        headers = list(records[0].keys())
        rows: list[list[object]] = [[cast(object, header) for header in headers]]
        for record in records:
            if list(record.keys()) != headers:
                msg = "All records must have the same keys and key order"
                raise SheetAccessError(msg)
            rows.append([record[header] for header in headers])

        try:
            worksheet.clear()
            worksheet.update(rows, value_input_option="USER_ENTERED")
        except APIError as exc:
            msg = f"Google Sheets API error while writing worksheet: {worksheet_name}"
            raise SheetAccessError(msg) from exc

    def clear_worksheet(self, worksheet_name: str) -> None:
        try:
            self.get_worksheet(worksheet_name).clear()
        except SheetsError:
            raise
        except APIError as exc:
            msg = f"Google Sheets API error while clearing worksheet: {worksheet_name}"
            raise SheetAccessError(msg) from exc

    def health_check(self) -> bool:
        try:
            _ = self._get_spreadsheet().title
        except SheetsError:
            return False
        except (APIError, SpreadsheetNotFound, ValueError, json.JSONDecodeError):
            return False
        return True

    def _get_spreadsheet(self) -> SpreadsheetProtocol:
        if self._spreadsheet is None:
            try:
                self._spreadsheet = self._get_gspread_client().open_by_key(self._sheet_id)
            except SpreadsheetNotFound as exc:
                msg = f"Google spreadsheet not found: {self._sheet_id}"
                raise SheetAccessError(msg) from exc
            except APIError as exc:
                msg = f"Google Sheets API error while opening spreadsheet: {self._sheet_id}"
                raise SheetAccessError(msg) from exc
        return self._spreadsheet

    def _get_gspread_client(self) -> GSpreadClientProtocol:
        if self._gspread_client is None:
            try:
                service_account_info = json.loads(self._service_account_json)
            except json.JSONDecodeError as exc:
                msg = "GOOGLE_SERVICE_ACCOUNT_JSON must be valid JSON"
                raise SheetAccessError(msg) from exc

            if not isinstance(service_account_info, dict):
                msg = "GOOGLE_SERVICE_ACCOUNT_JSON must contain a JSON object"
                raise SheetAccessError(msg)

            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=SCOPES,
            )
            self._gspread_client = cast(GSpreadClientProtocol, gspread.authorize(credentials))
        return self._gspread_client
