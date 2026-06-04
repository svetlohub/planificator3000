from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.domain.task import Task


class Backlog(BaseModel):
    """Ordered collection of tasks that are known but not necessarily planned."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tasks: list[Task] = Field(default_factory=list)

    @computed_field(return_type=int)
    @property
    def tasks_count(self) -> int:
        return len(self.tasks)

    @computed_field(return_type=float)
    @property
    def total_estimate_hours(self) -> float:
        return sum(task.estimate_hours for task in self.tasks)
