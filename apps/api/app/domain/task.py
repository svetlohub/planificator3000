from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
)

from app.domain.enums import TaskSource, TaskStatus

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
WeekRef = Annotated[str, StringConstraints(pattern=r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")]
Hours = Annotated[float, Field(ge=0)]


class Task(BaseModel):
    """A normalized task contract consumed by planning-adjacent use cases."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    task_id: NonEmptyString
    title: NonEmptyString = Field(max_length=240)
    source: TaskSource
    status: TaskStatus
    owner: NonEmptyString
    assignee: NonEmptyString | None = None
    estimate_hours: Hours
    task_type: NonEmptyString
    week_ref: WeekRef

    @field_validator("estimate_hours")
    @classmethod
    def estimate_has_quarter_hour_precision(cls, value: float) -> float:
        if (value * 4) % 1 != 0:
            msg = "estimate_hours must use 0.25 hour precision"
            raise ValueError(msg)
        return value

    @computed_field(return_type=bool)
    @property
    def is_completed(self) -> bool:
        return self.status is TaskStatus.DONE

    @computed_field(return_type=bool)
    @property
    def is_assigned(self) -> bool:
        return self.assignee is not None
