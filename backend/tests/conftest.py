"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """An in-process HTTP client. No server needs to be running."""
    return TestClient(app)
