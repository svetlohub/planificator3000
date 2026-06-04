from math import isclose
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    model_validator,
)

from app.domain.task import Task

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Hours = Annotated[float, Field(ge=0)]


class Allocation(BaseModel):
    """Tasks and hours allocated to one assignee."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    assignee: NonEmptyString
    tasks: list[Task] = Field(default_factory=list)
    allocated_hours: Hours

    @model_validator(mode="after")
    def allocation_matches_tasks(self) -> Self:
        mismatched_task_ids = [
            task.task_id for task in self.tasks if task.assignee != self.assignee
        ]
        if mismatched_task_ids:
            msg = (
                f"all tasks must be assigned to {self.assignee}; mismatched: {mismatched_task_ids}"
            )
            raise ValueError(msg)

        expected_hours = sum(task.estimate_hours for task in self.tasks)
        if not isclose(self.allocated_hours, expected_hours, abs_tol=0.001):
            msg = "allocated_hours must equal the sum of task estimates"
            raise ValueError(msg)
        return self

    @computed_field(return_type=int)
    @property
    def tasks_count(self) -> int:
        return len(self.tasks)
