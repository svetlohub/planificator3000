import pytest
from app.domain import Task, TaskSource, TaskStatus, TeamMember


@pytest.fixture
def task() -> Task:
    return Task(
        task_id="task-001",
        title="Prepare monthly planning input",
        source=TaskSource.MONTHLY,
        status=TaskStatus.PLANNED,
        owner="Irina",
        assignee="Alex",
        estimate_hours=6.5,
        task_type="planning",
        week_ref="2026-W23",
    )


@pytest.fixture
def completed_task() -> Task:
    return Task(
        task_id="task-002",
        title="Close carry-over report",
        source=TaskSource.CARRY_OVER,
        status=TaskStatus.DONE,
        owner="Irina",
        assignee="Alex",
        estimate_hours=2.0,
        task_type="reporting",
        week_ref="2026-W23",
    )


@pytest.fixture
def team_member() -> TeamMember:
    return TeamMember(
        name="Alex",
        weekly_capacity_hours=40,
        reserved_buffer_percent=20,
        skills=["Python", "Planning"],
    )
