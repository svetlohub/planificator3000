from enum import StrEnum


class TaskSource(StrEnum):
    """Origin of a task before it enters the weekly planning flow."""

    COMPLETED = "completed"
    MONTHLY = "monthly"
    RECURRING = "recurring"
    CARRY_OVER = "carry_over"


class TaskStatus(StrEnum):
    """Lifecycle status represented by the domain contract."""

    DONE = "done"
    PENDING = "pending"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
