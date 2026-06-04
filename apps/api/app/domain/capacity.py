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

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Hours = Annotated[float, Field(ge=0)]


class Capacity(BaseModel):
    """Weekly capacity snapshot for a single team member."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    member_name: NonEmptyString
    total_hours: Hours
    buffer_hours: Hours
    available_hours: Hours

    @model_validator(mode="after")
    def available_hours_matches_total_minus_buffer(self) -> Self:
        expected_available = self.total_hours - self.buffer_hours
        if expected_available < 0:
            msg = "buffer_hours cannot exceed total_hours"
            raise ValueError(msg)
        if not isclose(self.available_hours, expected_available, abs_tol=0.001):
            msg = "available_hours must equal total_hours minus buffer_hours"
            raise ValueError(msg)
        return self

    @computed_field(return_type=float)
    @property
    def buffer_percent(self) -> float:
        if self.total_hours == 0:
            return 0
        return self.buffer_hours / self.total_hours * 100
