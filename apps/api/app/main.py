from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.connectors.sheets import (
    GoogleSheetsClient,
    InvalidSheetDataError,
    SheetAccessError,
    SheetsError,
    SheetsRepository,
    WorksheetNotFoundError,
)
from app.exception_handlers import (
    invalid_sheet_data_handler,
    sheet_access_error_handler,
    sheets_error_handler,
    worksheet_not_found_handler,
)
from app.routers import health, plans, smoke


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Initialise infrastructure on startup, release on shutdown.

    Google Sheets client is created only when credentials are present.
    The application starts successfully without credentials so that the
    health endpoint remains available in local / CI environments.
    """
    settings = get_settings()

    if settings.sheets_configured:
        # google_sheet_id / google_service_account_json are confirmed non-None
        # by sheets_configured, but mypy needs the explicit assert.
        assert settings.google_sheet_id is not None  # noqa: S101
        assert settings.google_service_account_json is not None  # noqa: S101

        client = GoogleSheetsClient(
            sheet_id=settings.google_sheet_id,
            service_account_json=settings.google_service_account_json,
        )
        app.state.sheets_repository = SheetsRepository(client=client, settings=settings)
    else:
        app.state.sheets_repository = None

    yield

    # Nothing to tear down for gspread (stateless HTTP session).


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.app_env == "local" else None,
        redoc_url="/redoc" if settings.app_env == "local" else None,
    )

    # ------------------------------------------------------------------ CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------- Exception handlers
    # Registered most-specific first so FastAPI matches precisely.
    app.add_exception_handler(WorksheetNotFoundError, worksheet_not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(SheetAccessError, sheet_access_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(InvalidSheetDataError, invalid_sheet_data_handler)  # type: ignore[arg-type]
    app.add_exception_handler(SheetsError, sheets_error_handler)  # type: ignore[arg-type]

    # --------------------------------------------------------------- Routers
    app.include_router(health.router, prefix=settings.api_prefix)
    app.include_router(smoke.router, prefix=settings.api_prefix)
    app.include_router(plans.router, prefix=settings.api_prefix)

    return app


app = create_app()
