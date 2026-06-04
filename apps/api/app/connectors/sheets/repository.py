from typing import Any, Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from app.config import Settings
from app.connectors.sheets.exceptions import InvalidSheetDataError
from app.connectors.sheets.schemas import (
    CompletedTaskRow,
    ConfigRow,
    MonthlyPlanRow,
    RecurringTaskRow,
    TeamRosterRow,
)

RowT = TypeVar("RowT", bound=BaseModel)


class SheetsClientProtocol(Protocol):
    def read_records(self, worksheet_name: str) -> list[dict[str, Any]]: ...

    def health_check(self) -> bool: ...


class SheetsRepository:
    """Repository that returns raw DTOs from configured Google worksheets."""

    def __init__(self, client: SheetsClientProtocol, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    def load_completed_tasks(self) -> list[CompletedTaskRow]:
        return self._load_rows(self._settings.google_worksheet_completed_tasks, CompletedTaskRow)

    def load_monthly_plan(self) -> list[MonthlyPlanRow]:
        return self._load_rows(self._settings.google_worksheet_monthly_plan, MonthlyPlanRow)

    def load_recurring_tasks(self) -> list[RecurringTaskRow]:
        return self._load_rows(self._settings.google_worksheet_recurring_tasks, RecurringTaskRow)

    def load_team_roster(self) -> list[TeamRosterRow]:
        return self._load_rows(self._settings.google_worksheet_team_roster, TeamRosterRow)

    def load_config(self) -> list[ConfigRow]:
        return self._load_rows(self._settings.google_worksheet_config, ConfigRow)

    def health_check(self) -> bool:
        return self._client.health_check()

    def _load_rows(self, worksheet_name: str, row_factory: type[RowT]) -> list[RowT]:
        raw_records = self._client.read_records(worksheet_name)
        rows: list[RowT] = []
        for index, raw_record in enumerate(raw_records, start=2):
            rows.append(self._validate_row(worksheet_name, index, raw_record, row_factory))
        return rows

    @staticmethod
    def _validate_row(
        worksheet_name: str,
        row_number: int,
        raw_record: dict[str, Any],
        row_factory: type[RowT],
    ) -> RowT:
        try:
            return row_factory.model_validate(raw_record)
        except ValidationError as exc:
            msg = f"Invalid data in worksheet {worksheet_name!r}, row {row_number}"
            raise InvalidSheetDataError(msg) from exc
