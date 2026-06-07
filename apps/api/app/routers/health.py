from typing import Literal

from fastapi import APIRouter, Depends, Request

from app.config import Settings, get_settings
from app.connectors.sheets import SheetsRepository
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


class DetailedHealthResponse(HealthResponse):
    sheets_configured: bool
    sheets_healthy: bool | None


@router.get("/health", response_model=DetailedHealthResponse)
def health(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> DetailedHealthResponse:
    repository: SheetsRepository | None = getattr(request.app.state, "sheets_repository", None)

    sheets_configured = settings.sheets_configured
    sheets_healthy: bool | None = None

    if repository is not None:
        try:
            sheets_healthy = repository.health_check()
        except Exception:  # noqa: BLE001
            sheets_healthy = False

    return DetailedHealthResponse(
        service=settings.app_name,
        environment=settings.app_env,
        sheets_configured=sheets_configured,
        sheets_healthy=sheets_healthy,
    )
