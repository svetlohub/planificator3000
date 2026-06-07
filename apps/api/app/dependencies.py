from typing import Annotated

from fastapi import Depends, HTTPException, Request

from app.config import Settings, get_settings
from app.connectors.sheets import SheetsRepository


def get_sheets_repository(request: Request) -> SheetsRepository:
    """
    Retrieve the SheetsRepository stored in app.state.

    Raises 503 if the repository was not initialised (missing credentials).
    """
    repository: SheetsRepository | None = getattr(request.app.state, "sheets_repository", None)
    if repository is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Google Sheets integration is not configured. "
                "Set GOOGLE_SHEET_ID and GOOGLE_SERVICE_ACCOUNT_JSON."
            ),
        )
    return repository


SheetsRepositoryDep = Annotated[SheetsRepository, Depends(get_sheets_repository)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
