import pytest
from app.domain import Task, TaskSource, TaskStatus
from pydantic import ValidationError


def test_task_computed_properties(task: Task) -> None:
    assert task.is_assigned is True
    assert task.is_completed is False


def test_completed_task_computed_property(completed_task: Task) -> None:
    assert completed_task.is_completed is True


def test_task_rejects_invalid_week_ref(task: Task) -> None:
    payload = task.model_dump(mode="python")
    payload["week_ref"] = "2026-23"

    with pytest.raises(ValidationError, match="week_ref"):
        Task.model_validate(payload)


def test_task_rejects_non_quarter_hour_estimate(task: Task) -> None:
    payload = task.model_dump(mode="python")
    payload["estimate_hours"] = 1.3

    with pytest.raises(ValidationError, match="0.25 hour precision"):
        Task.model_validate(payload)


def test_task_serializes_enum_values(task: Task) -> None:
    payload = task.model_dump(mode="json")

    assert payload["source"] == TaskSource.MONTHLY.value
    assert payload["status"] == TaskStatus.PLANNED.value
    assert payload["is_assigned"] is True
