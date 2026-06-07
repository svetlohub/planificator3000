from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.domain import Task, TeamMember

PlanStatus = Literal["draft", "active", "completed"]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    environment: str


class Plan(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=140)
    status: PlanStatus = "draft"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CurrentPlanResponse(BaseModel):
    """Response body for GET /api/v1/plans/current."""

    model_config = ConfigDict(frozen=True)

    tasks: list[Task]
    team: list[TeamMember]
    sheets_configured: bool
