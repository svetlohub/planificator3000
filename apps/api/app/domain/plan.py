from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    model_validator,
)

from app.domain.enums import TaskStatus
from app.domain.task import Task

WeekRef = Annotated[str, StringConstraints(pattern=r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")]


class WeeklyPlan(BaseModel):
    """Task collection for one ISO-like planning week."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    week_ref: WeekRef
    tasks: list[Task] = Field(default_factory=list)

    @model_validator(mode="after")
    def task_weeks_match_plan_week(self) -> Self:
        mismatched_task_ids = [
            task.task_id for task in self.tasks if task.week_ref != self.week_ref
        ]
        if mismatched_task_ids:
            msg = f"all tasks must have week_ref={self.week_ref}; mismatched: {mismatched_task_ids}"
            raise ValueError(msg)
        return self

    @computed_field(return_type=float)
    @property
    def total_estimate_hours(self) -> float:
        return sum(task.estimate_hours for task in self.tasks)

    @computed_field(return_type=int)
    @property
    def planned_tasks_count(self) -> int:
        return sum(task.status is TaskStatus.PLANNED for task in self.tasks)

    @computed_field(return_type=int)
    @property
    def completed_tasks_count(self) -> int:
        return sum(task.status is TaskStatus.DONE for task in self.tasks)
