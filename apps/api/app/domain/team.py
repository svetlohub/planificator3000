from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
)

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Hours = Annotated[float, Field(ge=0)]
Percent = Annotated[float, Field(ge=0, le=100)]


class TeamMember(BaseModel):
    """A team member with weekly capacity and domain-level skill tags."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    name: NonEmptyString
    weekly_capacity_hours: Hours
    reserved_buffer_percent: Percent = 0
    skills: list[NonEmptyString] = Field(default_factory=list)

    @field_validator("skills")
    @classmethod
    def normalize_unique_skills(cls, value: list[str]) -> list[str]:
        normalized = [skill.strip().lower() for skill in value]
        if len(normalized) != len(set(normalized)):
            msg = "skills must be unique after normalization"
            raise ValueError(msg)
        return normalized

    @computed_field(return_type=float)
    @property
    def buffer_hours(self) -> float:
        return self.weekly_capacity_hours * self.reserved_buffer_percent / 100

    @computed_field(return_type=float)
    @property
    def available_capacity_hours(self) -> float:
        return self.weekly_capacity_hours - self.buffer_hours
