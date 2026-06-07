"""
Tests for Planner.

Covers:
- Recurring tasks always included
- Monthly tasks always included
- Completed-source DONE tasks excluded
- Completed-source non-DONE tasks included
- Deduplication by task_id (recurring wins)
- Ordering: week_ref asc, then estimate_hours asc
- Empty inputs
- Determinism: same input → same output on repeated calls
"""

import pytest
from app.domain import Task, TaskSource, TaskStatus
from app.services.planner import Planner


# ─────────────────────────────── helpers


def _task(
    task_id: str,
    source: TaskSource,
    status: TaskStatus = TaskStatus.PLANNED,
    estimate: float = 2.0,
    week_ref: str = "2026-W25",
    owner: str = "Ivan",
) -> Task:
    return Task(
        task_id=task_id,
        title=f"Task {task_id}",
        source=source,
        status=status,
        owner=owner,
        estimate_hours=estimate,
        task_type="analysis",
        week_ref=week_ref,
    )


def _recurring(task_id: str, estimate: float = 1.0, week_ref: str = "2026-W25") -> Task:
    return _task(task_id, TaskSource.RECURRING, TaskStatus.PENDING, estimate, week_ref)


def _monthly(task_id: str, estimate: float = 2.0, week_ref: str = "2026-W25") -> Task:
    return _task(task_id, TaskSource.MONTHLY, TaskStatus.PLANNED, estimate, week_ref)


def _completed_done(task_id: str) -> Task:
    return _task(task_id, TaskSource.COMPLETED, TaskStatus.DONE)


def _completed_pending(task_id: str, estimate: float = 1.5) -> Task:
    return _task(task_id, TaskSource.COMPLETED, TaskStatus.PENDING, estimate)


# ─────────────────────────────── basic inclusion


def test_recurring_tasks_always_included() -> None:
    candidates = Planner().build_candidates(
        monthly_tasks=[],
        completed_tasks=[],
        recurring_tasks=[_recurring("R1")],
    )
    assert any(t.task_id == "R1" for t in candidates)


def test_monthly_tasks_always_included() -> None:
    candidates = Planner().build_candidates(
        monthly_tasks=[_monthly("M1")],
        completed_tasks=[],
        recurring_tasks=[],
    )
    assert any(t.task_id == "M1" for t in candidates)


def test_completed_done_tasks_excluded() -> None:
    candidates = Planner().build_candidates(
        monthly_tasks=[],
        completed_tasks=[_completed_done("D1")],
        recurring_tasks=[],
    )
    assert not any(t.task_id == "D1" for t in candidates)


def test_completed_pending_tasks_included() -> None:
    candidates = Planner().build_candidates(
        monthly_tasks=[],
        completed_tasks=[_completed_pending("P1")],
        recurring_tasks=[],
    )
    assert any(t.task_id == "P1" for t in candidates)


def test_completed_in_progress_tasks_included() -> None:
    task = _task("IP1", TaskSource.COMPLETED, TaskStatus.IN_PROGRESS)
    candidates = Planner().build_candidates(
        monthly_tasks=[],
        completed_tasks=[task],
        recurring_tasks=[],
    )
    assert any(t.task_id == "IP1" for t in candidates)


# ─────────────────────────────── empty inputs


def test_all_empty_inputs_returns_empty() -> None:
    candidates = Planner().build_candidates(
        monthly_tasks=[],
        completed_tasks=[],
        recurring_tasks=[],
    )
    assert candidates == []


def test_only_done_tasks_returns_empty() -> None:
    candidates = Planner().build_candidates(
        monthly_tasks=[],
        completed_tasks=[_completed_done("D1"), _completed_done("D2")],
        recurring_tasks=[],
    )
    assert candidates == []


# ─────────────────────────────── deduplication


def test_recurring_wins_dedup_over_monthly() -> None:
    """Same task_id in recurring and monthly: recurring version is kept."""
    recurring = _recurring("SHARED")
    monthly = _monthly("SHARED")

    candidates = Planner().build_candidates(
        monthly_tasks=[monthly],
        completed_tasks=[],
        recurring_tasks=[recurring],
    )
    ids = [t.task_id for t in candidates]
    assert ids.count("SHARED") == 1
    match = next(t for t in candidates if t.task_id == "SHARED")
    assert match.source is TaskSource.RECURRING


def test_monthly_dedup_over_completed() -> None:
    """Same task_id in monthly and completed: monthly version is kept."""
    monthly = _monthly("SHARED")
    completed = _completed_pending("SHARED")

    candidates = Planner().build_candidates(
        monthly_tasks=[monthly],
        completed_tasks=[completed],
        recurring_tasks=[],
    )
    ids = [t.task_id for t in candidates]
    assert ids.count("SHARED") == 1
    match = next(t for t in candidates if t.task_id == "SHARED")
    assert match.source is TaskSource.MONTHLY


# ─────────────────────────────── ordering


def test_tasks_sorted_by_week_ref_ascending() -> None:
    t1 = _monthly("M1", week_ref="2026-W26")
    t2 = _monthly("M2", week_ref="2026-W24")
    t3 = _monthly("M3", week_ref="2026-W25")

    candidates = Planner().build_candidates(
        monthly_tasks=[t1, t2, t3],
        completed_tasks=[],
        recurring_tasks=[],
    )
    week_refs = [t.week_ref for t in candidates]
    assert week_refs == ["2026-W24", "2026-W25", "2026-W26"]


def test_tasks_sorted_by_estimate_within_same_week() -> None:
    t1 = _monthly("M1", estimate=4.0, week_ref="2026-W25")
    t2 = _monthly("M2", estimate=1.0, week_ref="2026-W25")
    t3 = _monthly("M3", estimate=2.0, week_ref="2026-W25")

    candidates = Planner().build_candidates(
        monthly_tasks=[t1, t2, t3],
        completed_tasks=[],
        recurring_tasks=[],
    )
    estimates = [t.estimate_hours for t in candidates]
    assert estimates == [1.0, 2.0, 4.0]


def test_sort_is_stable_across_sources() -> None:
    """Recurring + monthly with same week: recurring sorted by estimate too."""
    r1 = _recurring("R1", estimate=3.0, week_ref="2026-W25")
    m1 = _monthly("M1", estimate=1.0, week_ref="2026-W25")

    candidates = Planner().build_candidates(
        monthly_tasks=[m1],
        completed_tasks=[],
        recurring_tasks=[r1],
    )
    assert candidates[0].task_id == "M1"
    assert candidates[1].task_id == "R1"


# ─────────────────────────────── determinism


def test_same_input_produces_same_output() -> None:
    monthly = [_monthly(f"M{i}", estimate=float(i), week_ref="2026-W25") for i in range(1, 6)]
    planner = Planner()

    first = planner.build_candidates(monthly_tasks=monthly, completed_tasks=[], recurring_tasks=[])
    second = planner.build_candidates(monthly_tasks=monthly, completed_tasks=[], recurring_tasks=[])

    assert [t.task_id for t in first] == [t.task_id for t in second]
