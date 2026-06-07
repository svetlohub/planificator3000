from fastapi import Request
from fastapi.responses import JSONResponse

from app.connectors.sheets.exceptions import (
    InvalidSheetDataError,
    SheetAccessError,
    SheetsError,
    WorksheetNotFoundError,
)


async def sheets_error_handler(request: Request, exc: SheetsError) -> JSONResponse:
    """Catch-all for any unhandled SheetsError subclass."""
    return JSONResponse(
        status_code=503,
        content={"detail": "Google Sheets service unavailable", "error": str(exc)},
    )


async def sheet_access_error_handler(request: Request, exc: SheetAccessError) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": "Cannot access Google Sheets", "error": str(exc)},
    )


async def worksheet_not_found_handler(
    request: Request, exc: WorksheetNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": "Configured worksheet not found", "error": str(exc)},
    )


async def invalid_sheet_data_handler(
    request: Request, exc: InvalidSheetDataError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid data in Google Sheets", "error": str(exc)},
    )
