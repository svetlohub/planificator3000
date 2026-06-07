"""
Output schemas produced by the PlanningOrchestrator.

These are pure Pydantic v2 models with no FastAPI or Sheets dependencies.
They are used by the API layer as response models without modification.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.domain import Allocation, Backlog, Capacity, Task

WeekRef = Annotated[str, StringConstraints(pattern=r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")]


class WeeklyPlanResult(BaseModel):
    """Complete output of one planning cycle."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    week_ref: WeekRef
    scheduled_tasks: list[Task] = Field(default_factory=list)
    backlog_tasks: list[Task] = Field(default_factory=list)
    allocations: list[Allocation] = Field(default_factory=list)
    team_capacity: list[Capacity] = Field(default_factory=list)
    total_capacity_hours: float = Field(ge=0)
    planned_hours: float = Field(ge=0)
    backlog_hours: float = Field(ge=0)

    @model_validator(mode="after")
    def planned_hours_matches_scheduled(self) -> "WeeklyPlanResult":
        expected = round(sum(t.estimate_hours for t in self.scheduled_tasks), 10)
        if round(self.planned_hours, 10) != expected:
            msg = (
                f"planned_hours ({self.planned_hours}) must equal "
                f"sum of scheduled_tasks estimates ({expected})"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def backlog_hours_matches_backlog_tasks(self) -> "WeeklyPlanResult":
        expected = round(sum(t.estimate_hours for t in self.backlog_tasks), 10)
        if round(self.backlog_hours, 10) != expected:
            msg = (
                f"backlog_hours ({self.backlog_hours}) must equal "
                f"sum of backlog_tasks estimates ({expected})"
            )
            raise ValueError(msg)
        return self
