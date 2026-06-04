from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
)

WeekRef = Annotated[str, StringConstraints(pattern=r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")]
SummaryLine = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class WeeklyReport(BaseModel):
    """Read-model contract for a weekly planning report."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    week_ref: WeekRef
    completed_tasks_count: int = Field(ge=0)
    active_tasks_count: int = Field(ge=0)
    summary_lines: list[SummaryLine] = Field(default_factory=list)

    @field_validator("summary_lines")
    @classmethod
    def summary_lines_are_unique(cls, value: list[str]) -> list[str]:
        normalized = [line.strip() for line in value]
        if len(normalized) != len(set(normalized)):
            msg = "summary_lines must be unique"
            raise ValueError(msg)
        return normalized

    @computed_field(return_type=int)
    @property
    def total_referenced_tasks_count(self) -> int:
        return self.completed_tasks_count + self.active_tasks_count

    @computed_field(return_type=bool)
    @property
    def has_activity(self) -> bool:
        return self.total_referenced_tasks_count > 0 or bool(self.summary_lines)
