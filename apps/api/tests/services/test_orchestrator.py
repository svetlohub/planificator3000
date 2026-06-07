"""
Tests for PlanningOrchestrator.

Covers end-to-end planning flow using only in-memory domain objects.
No Google Sheets, no FastAPI.
"""

import pytest
from app.connectors.sheets.schemas import ConfigRow
from app.domain import Task, TaskSource, TaskStatus, TeamMember
from app.services.orchestrator import PlanningOrchestrator
from app.services.schemas import WeeklyPlanResult

WEEK = "2026-W25"


# ─────────────────────────────── helpers


def _member(name: str, hours: float, buffer_pct: float = 25.0) -> TeamMember:
    return TeamMember(
        name=name,
        weekly_capacity_hours=hours,
        reserved_buffer_percent=buffer_pct,
    )


def _monthly_task(task_id: str, estimate: float, owner: str = "Ivan") -> Task:
    return Task(
        task_id=task_id,
        title=f"Monthly {task_id}",
        source=TaskSource.MONTHLY,
        status=TaskStatus.PLANNED,
        owner=owner,
        estimate_hours=estimate,
        task_type="analysis",
        week_ref=WEEK,
    )


def _recurring_task(task_id: str, estimate: float, owner: str = "Ivan") -> Task:
    return Task(
        task_id=task_id,
        title=f"Recurring {task_id}",
        source=TaskSource.RECURRING,
        status=TaskStatus.PENDING,
        owner=owner,
        estimate_hours=estimate,
        task_type="meeting",
        week_ref=WEEK,
    )


def _completed_done(task_id: str) -> Task:
    return Task(
        task_id=task_id,
        title=f"Done {task_id}",
        source=TaskSource.COMPLETED,
        status=TaskStatus.DONE,
        owner="Ivan",
        estimate_hours=1.0,
        task_type="routine",
        week_ref=WEEK,
    )


def _config_row(key: str, value: str) -> ConfigRow:
    return ConfigRow.model_validate({"Key": key, "Value": value})


def _run(
    monthly: list[Task] | None = None,
    completed: list[Task] | None = None,
    recurring: list[Task] | None = None,
    members: list[TeamMember] | None = None,
    config: list[ConfigRow] | None = None,
) -> WeeklyPlanResult:
    return PlanningOrchestrator().generate_weekly_plan(
        week_ref=WEEK,
        monthly_tasks=monthly or [],
        completed_tasks=completed or [],
        recurring_tasks=recurring or [],
        team_members=members or [],
        config_rows=config or [],
    )


# ─────────────────────────────── result shape


def test_result_is_weekly_plan_result_instance() -> None:
    result = _run()
    assert isinstance(result, WeeklyPlanResult)


def test_result_week_ref_matches_input() -> None:
    result = _run()
    assert result.week_ref == WEEK


def test_empty_inputs_produce_empty_result() -> None:
    result = _run()
    assert result.scheduled_tasks == []
    assert result.backlog_tasks == []
    assert result.allocations == []
    assert result.total_capacity_hours == 0.0
    assert result.planned_hours == 0.0
    assert result.backlog_hours == 0.0


# ─────────────────────────────── capacity pipeline


def test_team_capacity_included_in_result() -> None:
    members = [_member("Ivan", 40)]
    result = _run(members=members)

    assert len(result.team_capacity) == 1
    assert result.team_capacity[0].member_name == "Ivan"


def test_total_capacity_hours_aggregated() -> None:
    # Ivan: 40h * 0.75 = 30h, Maria: 32h * 0.75 = 24h → total 54h
    members = [_member("Ivan", 40), _member("Maria", 32)]
    result = _run(members=members)

    assert result.total_capacity_hours == pytest.approx(54.0)


def test_config_buffer_flows_into_capacity() -> None:
    members = [_member("Ivan", 40, buffer_pct=0)]  # 0 = use global
    config = [_config_row("buffer_percent", "20")]

    result = _run(members=members, config=config)

    assert result.team_capacity[0].available_hours == pytest.approx(32.0)


# ─────────────────────────────── scheduling


def test_scheduled_tasks_not_in_backlog() -> None:
    members = [_member("Ivan", 40)]
    tasks = [_monthly_task("M1", 2.0, owner="Ivan")]

    result = _run(monthly=tasks, members=members)

    scheduled_ids = {t.task_id for t in result.scheduled_tasks}
    backlog_ids = {t.task_id for t in result.backlog_tasks}
    assert scheduled_ids.isdisjoint(backlog_ids)


def test_task_over_capacity_goes_to_backlog() -> None:
    members = [_member("Ivan", 4, buffer_pct=0)]  # 4h available
    tasks = [_monthly_task("BIG", 8.0, owner="Ivan")]  # 8h needed

    result = _run(monthly=tasks, members=members)

    assert any(t.task_id == "BIG" for t in result.backlog_tasks)
    assert not any(t.task_id == "BIG" for t in result.scheduled_tasks)


def test_recurring_tasks_scheduled_before_monthly() -> None:
    """Recurring tasks land in scheduled when capacity allows."""
    members = [_member("Ivan", 40)]
    recurring = [_recurring_task("R1", 1.0, owner="Ivan")]
    monthly = [_monthly_task("M1", 2.0, owner="Ivan")]

    result = _run(monthly=monthly, recurring=recurring, members=members)

    scheduled_ids = {t.task_id for t in result.scheduled_tasks}
    assert "R1" in scheduled_ids
    assert "M1" in scheduled_ids


def test_completed_done_tasks_not_in_candidates() -> None:
    members = [_member("Ivan", 40)]
    completed = [_completed_done("D1")]

    result = _run(completed=completed, members=members)

    all_ids = {t.task_id for t in result.scheduled_tasks + result.backlog_tasks}
    assert "D1" not in all_ids


# ─────────────────────────────── hours accounting


def test_planned_hours_equals_sum_of_scheduled() -> None:
    members = [_member("Ivan", 40)]
    tasks = [_monthly_task("M1", 2.0), _monthly_task("M2", 3.0)]

    result = _run(monthly=tasks, members=members)

    expected = sum(t.estimate_hours for t in result.scheduled_tasks)
    assert result.planned_hours == pytest.approx(expected)


def test_backlog_hours_equals_sum_of_backlog_tasks() -> None:
    members = [_member("Ivan", 2, buffer_pct=0)]  # only 2h
    tasks = [_monthly_task("M1", 2.0), _monthly_task("M2", 3.0)]

    result = _run(monthly=tasks, members=members)

    expected = sum(t.estimate_hours for t in result.backlog_tasks)
    assert result.backlog_hours == pytest.approx(expected)


# ─────────────────────────────── allocations


def test_allocations_cover_all_scheduled_tasks() -> None:
    members = [_member("Ivan", 40)]
    tasks = [_monthly_task(f"M{i}", 1.0) for i in range(3)]

    result = _run(monthly=tasks, members=members)

    allocated_task_ids = {t.task_id for a in result.allocations for t in a.tasks}
    scheduled_ids = {t.task_id for t in result.scheduled_tasks}
    assert allocated_task_ids == scheduled_ids


def test_allocations_never_exceed_member_capacity() -> None:
    members = [_member("Ivan", 10, buffer_pct=0)]  # 10h available
    tasks = [_monthly_task(f"M{i}", 2.0) for i in range(6)]  # 12h total

    result = _run(monthly=tasks, members=members)

    for allocation in result.allocations:
        member_cap = next(
            c for c in result.team_capacity if c.member_name == allocation.assignee
        )
        assert allocation.allocated_hours <= member_cap.available_hours + 1e-9


# ─────────────────────────────── no team scenario


def test_no_team_all_tasks_to_backlog() -> None:
    tasks = [_monthly_task("M1", 2.0), _monthly_task("M2", 1.0)]

    result = _run(monthly=tasks, members=[])

    assert len(result.backlog_tasks) == 2
    assert len(result.scheduled_tasks) == 0


# ─────────────────────────────── determinism


def test_orchestrator_is_deterministic() -> None:
    members = [_member("Ivan", 40), _member("Maria", 32)]
    tasks = [_monthly_task(f"M{i}", float(i % 4 + 1)) for i in range(8)]

    result1 = _run(monthly=tasks, members=members)
    result2 = _run(monthly=tasks, members=members)

    assert [t.task_id for t in result1.scheduled_tasks] == [
        t.task_id for t in result2.scheduled_tasks
    ]
    assert [t.task_id for t in result1.backlog_tasks] == [
        t.task_id for t in result2.backlog_tasks
    ]
