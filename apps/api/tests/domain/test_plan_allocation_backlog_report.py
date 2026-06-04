import pytest
from app.domain import Allocation, Backlog, Task, TaskStatus, WeeklyPlan, WeeklyReport
from pydantic import ValidationError


def test_weekly_plan_computed_properties(task: Task, completed_task: Task) -> None:
    plan = WeeklyPlan(week_ref="2026-W23", tasks=[task, completed_task])

    assert plan.total_estimate_hours == 8.5
    assert plan.planned_tasks_count == 1
    assert plan.completed_tasks_count == 1


def test_weekly_plan_rejects_tasks_from_another_week(task: Task) -> None:
    with pytest.raises(ValidationError, match="all tasks must have week_ref"):
        WeeklyPlan(week_ref="2026-W24", tasks=[task])


def test_allocation_validates_assignee_and_hours(task: Task, completed_task: Task) -> None:
    allocation = Allocation(assignee="Alex", tasks=[task, completed_task], allocated_hours=8.5)

    assert allocation.tasks_count == 2


def test_allocation_rejects_wrong_assignee(task: Task) -> None:
    with pytest.raises(ValidationError, match="all tasks must be assigned"):
        Allocation(assignee="Maria", tasks=[task], allocated_hours=6.5)


def test_allocation_rejects_wrong_hours(task: Task) -> None:
    with pytest.raises(ValidationError, match="allocated_hours"):
        Allocation(assignee="Alex", tasks=[task], allocated_hours=1)


def test_backlog_computed_properties(task: Task, completed_task: Task) -> None:
    backlog = Backlog(tasks=[task, completed_task])

    assert backlog.tasks_count == 2
    assert backlog.total_estimate_hours == 8.5


def test_weekly_report_computed_properties() -> None:
    report = WeeklyReport(
        week_ref="2026-W23",
        completed_tasks_count=3,
        active_tasks_count=5,
        summary_lines=["Shipped planning foundation"],
    )

    assert report.total_referenced_tasks_count == 8
    assert report.has_activity is True


def test_weekly_report_rejects_duplicate_summary_lines() -> None:
    with pytest.raises(ValidationError, match="summary_lines must be unique"):
        WeeklyReport(
            week_ref="2026-W23",
            completed_tasks_count=0,
            active_tasks_count=1,
            summary_lines=["Same", "Same"],
        )


def test_weekly_report_serialization() -> None:
    report = WeeklyReport(
        week_ref="2026-W23",
        completed_tasks_count=1,
        active_tasks_count=2,
        summary_lines=["All contracts serialized"],
    )

    assert report.model_dump(mode="json") == {
        "week_ref": "2026-W23",
        "completed_tasks_count": 1,
        "active_tasks_count": 2,
        "summary_lines": ["All contracts serialized"],
        "total_referenced_tasks_count": 3,
        "has_activity": True,
    }
    assert '"week_ref":"2026-W23"' in report.model_dump_json()


def test_plan_serialization_includes_nested_tasks(task: Task) -> None:
    plan = WeeklyPlan(week_ref="2026-W23", tasks=[task])
    payload = plan.model_dump(mode="json")

    assert payload["tasks"][0]["task_id"] == "task-001"
    assert payload["tasks"][0]["status"] == TaskStatus.PLANNED.value
    assert payload["total_estimate_hours"] == 6.5
