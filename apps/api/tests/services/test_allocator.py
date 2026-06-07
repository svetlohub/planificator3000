"""
Tests for Allocator.

Covers:
- Tasks assigned to least-loaded member
- Owner affinity: task goes to owner when owner has capacity
- Owner affinity fallback: task goes to another member when owner is full
- Capacity never exceeded
- Tasks go to backlog when no member can fit them
- Empty team → all tasks to backlog
- Empty tasks → empty allocations
- Multiple tasks per member
- Determinism
"""

import pytest
from app.domain import Capacity, Task, TaskSource, TaskStatus
from app.services.allocator import Allocator


# ─────────────────────────────── helpers


def _capacity(name: str, available: float) -> Capacity:
    total = available  # buffer=0 for simplicity in tests
    return Capacity(
        member_name=name,
        total_hours=total,
        buffer_hours=0.0,
        available_hours=available,
    )


def _task(
    task_id: str,
    estimate: float,
    owner: str = "Ivan",
    week_ref: str = "2026-W25",
) -> Task:
    return Task(
        task_id=task_id,
        title=f"Task {task_id}",
        source=TaskSource.MONTHLY,
        status=TaskStatus.PLANNED,
        owner=owner,
        estimate_hours=estimate,
        task_type="analysis",
        week_ref=week_ref,
    )


# ─────────────────────────────── basic allocation


def test_single_task_single_member_allocated() -> None:
    caps = [_capacity("Ivan", 8.0)]
    tasks = [_task("T1", 2.0, owner="Ivan")]

    allocations, backlog = Allocator().allocate(tasks, caps)

    assert len(allocations) == 1
    assert allocations[0].assignee == "Ivan"
    assert len(backlog) == 0


def test_allocated_hours_equals_task_estimate() -> None:
    caps = [_capacity("Ivan", 8.0)]
    tasks = [_task("T1", 3.0, owner="Ivan")]

    allocations, _ = Allocator().allocate(tasks, caps)

    assert allocations[0].allocated_hours == pytest.approx(3.0)


def test_empty_tasks_returns_empty_allocations() -> None:
    caps = [_capacity("Ivan", 8.0)]

    allocations, backlog = Allocator().allocate([], caps)

    assert allocations == []
    assert backlog == []


def test_empty_capacities_sends_all_to_backlog() -> None:
    tasks = [_task("T1", 2.0), _task("T2", 1.0)]

    allocations, backlog = Allocator().allocate(tasks, [])

    assert allocations == []
    assert len(backlog) == 2


# ─────────────────────────────── capacity enforcement


def test_task_exceeding_capacity_goes_to_backlog() -> None:
    caps = [_capacity("Ivan", 2.0)]
    tasks = [_task("T1", 5.0, owner="Ivan")]

    allocations, backlog = Allocator().allocate(tasks, caps)

    assert len(allocations) == 0
    assert backlog[0].task_id == "T1"


def test_allocated_hours_never_exceed_available() -> None:
    caps = [_capacity("Ivan", 6.0)]
    # Three tasks totalling 9h → only 6h fits
    tasks = [_task("T1", 2.0), _task("T2", 2.0), _task("T3", 2.0), _task("T4", 3.0)]

    allocations, backlog = Allocator().allocate(tasks, caps)

    total_allocated = sum(a.allocated_hours for a in allocations)
    assert total_allocated <= 6.0
    assert len(backlog) >= 1


def test_exact_capacity_fit_produces_no_backlog() -> None:
    caps = [_capacity("Ivan", 4.0)]
    tasks = [_task("T1", 2.0), _task("T2", 2.0)]

    allocations, backlog = Allocator().allocate(tasks, caps)

    assert len(backlog) == 0
    assert allocations[0].allocated_hours == pytest.approx(4.0)


# ─────────────────────────────── balanced allocation


def test_tasks_distributed_to_least_loaded_member() -> None:
    caps = [_capacity("Alice", 8.0), _capacity("Bob", 8.0)]
    # No owner affinity — both tasks should be split between members
    tasks = [
        _task("T1", 2.0, owner="Unknown"),
        _task("T2", 2.0, owner="Unknown"),
    ]

    allocations, backlog = Allocator().allocate(tasks, caps)

    assert len(backlog) == 0
    # Each member should have one task
    names = {a.assignee for a in allocations}
    assert "Alice" in names
    assert "Bob" in names


def test_load_balanced_across_three_members() -> None:
    caps = [_capacity("A", 8.0), _capacity("B", 8.0), _capacity("C", 8.0)]
    # 3 tasks × 2h each — one per member
    tasks = [_task(f"T{i}", 2.0, owner="Unknown") for i in range(3)]

    allocations, backlog = Allocator().allocate(tasks, caps)

    assert len(backlog) == 0
    hours = sorted(a.allocated_hours for a in allocations)
    assert hours == pytest.approx([2.0, 2.0, 2.0])


# ─────────────────────────────── owner affinity


def test_task_assigned_to_matching_owner_when_capacity_available() -> None:
    caps = [_capacity("Alice", 8.0), _capacity("Bob", 8.0)]
    tasks = [_task("T1", 3.0, owner="Alice")]

    allocations, backlog = Allocator().allocate(tasks, caps)

    assert len(backlog) == 0
    alice_alloc = next(a for a in allocations if a.assignee == "Alice")
    assert alice_alloc.allocated_hours == pytest.approx(3.0)


def test_task_falls_back_to_other_member_when_owner_at_capacity() -> None:
    caps = [_capacity("Alice", 1.0), _capacity("Bob", 8.0)]
    # Task is 3h; Alice only has 1h available
    tasks = [_task("T1", 3.0, owner="Alice")]

    allocations, backlog = Allocator().allocate(tasks, caps)

    assert len(backlog) == 0
    bob_alloc = next((a for a in allocations if a.assignee == "Bob"), None)
    assert bob_alloc is not None
    assert bob_alloc.allocated_hours == pytest.approx(3.0)


def test_task_goes_to_backlog_when_owner_missing_and_no_capacity() -> None:
    caps = [_capacity("Alice", 0.5)]
    tasks = [_task("T1", 3.0, owner="Charlie")]  # Charlie not in team

    allocations, backlog = Allocator().allocate(tasks, caps)

    assert len(backlog) == 1
    assert backlog[0].task_id == "T1"


# ─────────────────────────────── assigned task has assignee set


def test_allocated_task_has_assignee_field_set() -> None:
    caps = [_capacity("Ivan", 8.0)]
    tasks = [_task("T1", 2.0, owner="Ivan")]

    allocations, _ = Allocator().allocate(tasks, caps)

    assert allocations[0].tasks[0].assignee == "Ivan"


# ─────────────────────────────── backlog preservation


def test_backlog_preserves_original_task_metadata() -> None:
    caps = [_capacity("Ivan", 0.0)]  # no capacity
    original = _task("T1", 2.0, owner="Ivan")

    _, backlog = Allocator().allocate([original], caps)

    assert backlog[0].task_id == original.task_id
    assert backlog[0].title == original.title
    assert backlog[0].estimate_hours == original.estimate_hours


# ─────────────────────────────── only members with tasks produce allocations


def test_member_with_no_tasks_not_in_allocations() -> None:
    caps = [_capacity("Alice", 8.0), _capacity("Bob", 8.0)]
    tasks = [_task("T1", 2.0, owner="Alice")]

    allocations, _ = Allocator().allocate(tasks, caps)

    assignees = {a.assignee for a in allocations}
    assert "Bob" not in assignees


# ─────────────────────────────── determinism


def test_same_input_same_allocation_output() -> None:
    caps = [_capacity("A", 8.0), _capacity("B", 8.0)]
    tasks = [_task(f"T{i}", 1.0, owner="Unknown") for i in range(4)]
    allocator = Allocator()

    alloc1, back1 = allocator.allocate(tasks, caps)
    alloc2, back2 = allocator.allocate(tasks, caps)

    assert sorted(a.assignee for a in alloc1) == sorted(a.assignee for a in alloc2)
    assert [t.task_id for t in back1] == [t.task_id for t in back2]
