from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["smoke"])


class SmokeResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str = "PLANIFICATOR-3000 API"
    timestamp: str
    endpoints: dict[str, str]


@router.get("/smoke", response_model=SmokeResponse)
def smoke() -> SmokeResponse:
    return SmokeResponse(
        timestamp=datetime.now(UTC).isoformat(),
        endpoints={
            "health": "/api/health",
            "smoke": "/api/smoke",
            "plans": "/api/plans",
            "current_plan": "/api/plans/current",
            "generate_plan": "/api/plans/generate",
        },
    )
