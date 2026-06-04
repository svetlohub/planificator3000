from collections.abc import Iterable

from pydantic import ValidationError

from app.connectors.sheets.exceptions import InvalidSheetDataError
from app.connectors.sheets.schemas import (
    CompletedTaskRow,
    MonthlyPlanRow,
    RecurringTaskRow,
    TeamRosterRow,
)
from app.domain import Task, TaskSource, TaskStatus, TeamMember


class SheetsMapper:
    """Deterministic DTO-to-domain mapper without planner policy or fuzzy matching."""

    def completed_task_to_domain(self, row: CompletedTaskRow) -> Task:
        return self._task_from_row(row=row, source=TaskSource.COMPLETED, status=TaskStatus.DONE)

    def monthly_plan_to_domain(self, row: MonthlyPlanRow) -> Task:
        try:
            status = TaskStatus(row.status)
        except ValueError as exc:
            msg = f"Unsupported monthly plan status: {row.status}"
            raise InvalidSheetDataError(msg) from exc
        return self._task_from_row(row=row, source=TaskSource.MONTHLY, status=status)

    def recurring_task_to_domain(self, row: RecurringTaskRow) -> Task:
        return self._task_from_row(row=row, source=TaskSource.RECURRING, status=TaskStatus.PENDING)

    def team_member_to_domain(self, row: TeamRosterRow) -> TeamMember:
        skills = [skill.strip() for skill in row.skills.split(",") if skill.strip()]
        try:
            return TeamMember(
                name=row.name,
                weekly_capacity_hours=row.weekly_capacity_hours,
                reserved_buffer_percent=row.reserved_buffer_percent,
                skills=skills,
            )
        except ValidationError as exc:
            msg = f"Invalid team roster row for member: {row.name}"
            raise InvalidSheetDataError(msg) from exc

    def completed_tasks_to_domain(self, rows: Iterable[CompletedTaskRow]) -> list[Task]:
        return [self.completed_task_to_domain(row) for row in rows]

    def monthly_plan_to_domain_tasks(self, rows: Iterable[MonthlyPlanRow]) -> list[Task]:
        return [self.monthly_plan_to_domain(row) for row in rows]

    def recurring_tasks_to_domain(self, rows: Iterable[RecurringTaskRow]) -> list[Task]:
        return [self.recurring_task_to_domain(row) for row in rows]

    def team_roster_to_domain(self, rows: Iterable[TeamRosterRow]) -> list[TeamMember]:
        return [self.team_member_to_domain(row) for row in rows]

    @staticmethod
    def _task_from_row(
        row: CompletedTaskRow | MonthlyPlanRow | RecurringTaskRow,
        source: TaskSource,
        status: TaskStatus,
    ) -> Task:
        try:
            return Task(
                task_id=row.task_id,
                title=row.title,
                source=source,
                status=status,
                owner=row.owner,
                assignee=row.assignee or None,
                estimate_hours=row.estimate_hours,
                task_type=row.task_type,
                week_ref=row.week_ref,
            )
        except ValidationError as exc:
            msg = f"Invalid task row for task_id: {row.task_id}"
            raise InvalidSheetDataError(msg) from exc
