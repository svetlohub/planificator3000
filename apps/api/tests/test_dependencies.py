"""
Tests for dependency providers.

SheetsRepositoryDep must return the repository from app.state when present,
and raise 503 when it is absent (no credentials configured).
"""
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.connectors.sheets import SheetsRepository
from app.dependencies import SheetsRepositoryDep
from app.main import create_app


def _app_with_repository(repository: SheetsRepository | None) -> TestClient:
    app = create_app()
    app.state.sheets_repository = repository

    probe = APIRouter(prefix="/probe")

    @probe.get("/repo")
    def get_repo(repo: SheetsRepositoryDep) -> dict[str, str]:
        return {"ok": "true"}

    app.include_router(probe)
    return TestClient(app, raise_server_exceptions=False)


def _fake_repository() -> SheetsRepository:
    """Return a SheetsRepository backed by a stub client."""

    class _FakeClient:
        def read_records(self, _: str) -> list[dict[str, Any]]:
            return []

        def health_check(self) -> bool:
            return True

    from app.config import Settings

    return SheetsRepository(client=_FakeClient(), settings=Settings())


def test_dependency_returns_repository_when_configured() -> None:
    repo = _fake_repository()
    client = _app_with_repository(repo)

    response = client.get("/probe/repo")

    assert response.status_code == 200


def test_dependency_returns_503_when_repository_is_none() -> None:
    client = _app_with_repository(None)

    response = client.get("/probe/repo")

    assert response.status_code == 503
    assert "not configured" in response.json()["detail"].lower()
