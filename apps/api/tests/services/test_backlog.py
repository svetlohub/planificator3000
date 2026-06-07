"""
Tests for BacklogBuilder.

Covers:
- Empty input → empty Backlog
- Task metadata preserved exactly
- Order preserved
- Tasks not mutated
- Backlog computed fields correct
"""

from app.domain import Task, TaskSource, TaskStatus
from app.services.backlog import BacklogBuilder


def _task(task_id: str, estimate: float = 2.0) -> Task:
    return Task(
        task_id=task_id,
        title=f"Task {task_id}",
        source=TaskSource.MONTHLY,
        status=TaskStatus.PLANNED,
        owner="Ivan",
        estimate_hours=estimate,
        task_type="analysis",
        week_ref="2026-W25",
    )


# ─────────────────────────────── basic


def test_empty_input_returns_empty_backlog() -> None:
    backlog = BacklogBuilder().build([])

    assert backlog.tasks == []
    assert backlog.tasks_count == 0
    assert backlog.total_estimate_hours == 0.0


def test_single_task_in_backlog() -> None:
    task = _task("T1")
    backlog = BacklogBuilder().build([task])

    assert backlog.tasks_count == 1
    assert backlog.tasks[0].task_id == "T1"


# ─────────────────────────────── metadata preservation


def test_task_title_preserved() -> None:
    task = _task("T1")
    backlog = BacklogBuilder().build([task])

    assert backlog.tasks[0].title == task.title


def test_task_estimate_preserved() -> None:
    task = _task("T1", estimate=3.5)
    backlog = BacklogBuilder().build([task])

    assert backlog.tasks[0].estimate_hours == 3.5


def test_task_source_preserved() -> None:
    task = _task("T1")
    backlog = BacklogBuilder().build([task])

    assert backlog.tasks[0].source is TaskSource.MONTHLY


def test_task_status_preserved() -> None:
    task = _task("T1")
    backlog = BacklogBuilder().build([task])

    assert backlog.tasks[0].status is TaskStatus.PLANNED


def test_task_owner_preserved() -> None:
    task = _task("T1")
    backlog = BacklogBuilder().build([task])

    assert backlog.tasks[0].owner == "Ivan"


# ─────────────────────────────── order


def test_order_preserved() -> None:
    tasks = [_task("T3"), _task("T1"), _task("T2")]
    backlog = BacklogBuilder().build(tasks)

    assert [t.task_id for t in backlog.tasks] == ["T3", "T1", "T2"]


# ─────────────────────────────── computed fields


def test_total_estimate_hours_computed() -> None:
    tasks = [_task("T1", 2.0), _task("T2", 3.5), _task("T3", 1.0)]
    backlog = BacklogBuilder().build(tasks)

    assert backlog.total_estimate_hours == 6.5
    assert backlog.tasks_count == 3


# ─────────────────────────────── immutability


def test_original_list_not_mutated() -> None:
    original = [_task("T1"), _task("T2")]
    original_copy = list(original)
    BacklogBuilder().build(original)

    assert [t.task_id for t in original] == [t.task_id for t in original_copy]
