"""Shared pytest fixtures."""

import os
import sys
from pathlib import Path

import pytest

# Example app imports
EXAMPLE_DIR = Path(__file__).resolve().parent.parent / "example"
if str(EXAMPLE_DIR) not in sys.path:
    sys.path.insert(0, str(EXAMPLE_DIR))


@pytest.fixture(autouse=True)
def flask_base_env(monkeypatch):
    """Minimum env vars required by flask-base."""
    monkeypatch.setenv("FLASK_SECRET", "test-secret-key-for-pytest")
    monkeypatch.setenv("ADMIN_KEY", "test-admin-key")
    monkeypatch.setenv("FLASK_BASE_KEY_PREFIX", "EXAMPLE_KEY_")
    monkeypatch.setenv("EXAMPLE_KEY_ALICE", "alice-test-key:view")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
