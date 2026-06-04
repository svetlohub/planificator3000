import pytest
from app.connectors.sheets.schemas import (
    CompletedTaskRow,
    MonthlyPlanRow,
    RecurringTaskRow,
    TeamRosterRow,
)


@pytest.fixture
def completed_task_row() -> CompletedTaskRow:
    return CompletedTaskRow.model_validate(
        {
            "Task ID": "done-1",
            "Title": "Close weekly report",
            "Owner": "Irina",
            "Assignee": "Alex",
            "Estimate Hours": 2,
            "Task Type": "reporting",
            "Week": "2026-W23",
        },
    )


@pytest.fixture
def monthly_plan_row() -> MonthlyPlanRow:
    return MonthlyPlanRow.model_validate(
        {
            "Task ID": "monthly-1",
            "Title": "Prepare monthly plan",
            "Status": "planned",
            "Owner": "Irina",
            "Assignee": "Maria",
            "Estimate Hours": 4.5,
            "Task Type": "planning",
            "Week": "2026-W23",
        },
    )


@pytest.fixture
def recurring_task_row() -> RecurringTaskRow:
    return RecurringTaskRow.model_validate(
        {
            "Task ID": "recurring-1",
            "Title": "Refresh metrics",
            "Owner": "Irina",
            "Assignee": "Alex",
            "Estimate Hours": 1,
            "Task Type": "operations",
            "Week": "2026-W23",
        },
    )


@pytest.fixture
def team_roster_row() -> TeamRosterRow:
    return TeamRosterRow.model_validate(
        {
            "Name": "Alex",
            "Weekly Capacity Hours": 40,
            "Reserved Buffer Percent": 20,
            "Skills": "Python, Planning",
        },
    )
