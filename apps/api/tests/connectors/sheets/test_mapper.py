import pytest
from app.connectors.sheets import InvalidSheetDataError, SheetsMapper
from app.connectors.sheets.schemas import MonthlyPlanRow
from app.domain import TaskSource, TaskStatus


def test_completed_task_row_maps_to_completed_domain_task(completed_task_row) -> None:
    task = SheetsMapper().completed_task_to_domain(completed_task_row)

    assert task.task_id == "done-1"
    assert task.source is TaskSource.COMPLETED
    assert task.status is TaskStatus.DONE
    assert task.is_completed is True


def test_monthly_plan_row_maps_status_exactly(monthly_plan_row) -> None:
    task = SheetsMapper().monthly_plan_to_domain(monthly_plan_row)

    assert task.source is TaskSource.MONTHLY
    assert task.status is TaskStatus.PLANNED
    assert task.assignee == "Maria"


def test_monthly_plan_mapping_rejects_unknown_status(monthly_plan_row: MonthlyPlanRow) -> None:
    bad_row = monthly_plan_row.model_copy(update={"status": "almost_done"})

    with pytest.raises(InvalidSheetDataError, match="Unsupported monthly plan status"):
        SheetsMapper().monthly_plan_to_domain(bad_row)


def test_recurring_task_row_maps_to_pending_task(recurring_task_row) -> None:
    task = SheetsMapper().recurring_task_to_domain(recurring_task_row)

    assert task.source is TaskSource.RECURRING
    assert task.status is TaskStatus.PENDING


def test_team_roster_row_maps_skills_deterministically(team_roster_row) -> None:
    member = SheetsMapper().team_member_to_domain(team_roster_row)

    assert member.name == "Alex"
    assert member.weekly_capacity_hours == 40
    assert member.reserved_buffer_percent == 20
    assert member.skills == ["python", "planning"]
    assert member.available_capacity_hours == 32
