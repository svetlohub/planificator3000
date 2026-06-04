from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
OptionalString = Annotated[str, StringConstraints(strip_whitespace=True)]
Hours = Annotated[float, Field(ge=0)]
Percent = Annotated[float, Field(ge=0, le=100)]
WeekRef = Annotated[str, StringConstraints(pattern=r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")]


class SheetRow(BaseModel):
    """Base class for raw Google Sheets DTO rows."""

    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class CompletedTaskRow(SheetRow):
    task_id: NonEmptyString = Field(alias="Task ID")
    title: NonEmptyString = Field(alias="Title")
    owner: NonEmptyString = Field(alias="Owner")
    assignee: OptionalString | None = Field(default=None, alias="Assignee")
    estimate_hours: Hours = Field(alias="Estimate Hours")
    task_type: NonEmptyString = Field(alias="Task Type")
    week_ref: WeekRef = Field(alias="Week")


class MonthlyPlanRow(SheetRow):
    task_id: NonEmptyString = Field(alias="Task ID")
    title: NonEmptyString = Field(alias="Title")
    status: NonEmptyString = Field(default="pending", alias="Status")
    owner: NonEmptyString = Field(alias="Owner")
    assignee: OptionalString | None = Field(default=None, alias="Assignee")
    estimate_hours: Hours = Field(alias="Estimate Hours")
    task_type: NonEmptyString = Field(alias="Task Type")
    week_ref: WeekRef = Field(alias="Week")


class RecurringTaskRow(SheetRow):
    task_id: NonEmptyString = Field(alias="Task ID")
    title: NonEmptyString = Field(alias="Title")
    owner: NonEmptyString = Field(alias="Owner")
    assignee: OptionalString | None = Field(default=None, alias="Assignee")
    estimate_hours: Hours = Field(alias="Estimate Hours")
    task_type: NonEmptyString = Field(alias="Task Type")
    week_ref: WeekRef = Field(alias="Week")


class TeamRosterRow(SheetRow):
    name: NonEmptyString = Field(alias="Name")
    weekly_capacity_hours: Hours = Field(alias="Weekly Capacity Hours")
    reserved_buffer_percent: Percent = Field(default=0, alias="Reserved Buffer Percent")
    skills: str = Field(default="", alias="Skills")

    @field_validator("skills")
    @classmethod
    def strip_skills(cls, value: str) -> str:
        return value.strip()


class ConfigRow(SheetRow):
    key: NonEmptyString = Field(alias="Key")
    value: str = Field(default="", alias="Value")
