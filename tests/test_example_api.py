"""Tests for the example app API (Firestore mocked)."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def example_client():
    """Load example app with mocked Firestore."""
    import importlib
    import sys

    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.collection.return_value = mock_collection

    patch_target = "flask_base.firestore_setup.get_db"
    if "flask_base.flask_base" in sys.modules:
        patch_target = "flask_base.flask_base.firestore_setup.get_db"

    sys.modules.pop("app", None)
    with patch(patch_target, return_value=mock_db):
        import app as example_app

        example_app.app.config["TESTING"] = True
        client = example_app.app.test_client()
        yield client, mock_collection, example_app

    sys.modules.pop("app", None)


def test_list_notes_requires_auth(example_client):
    client, _, _ = example_client
    response = client.get("/api/notes")
    assert response.status_code == 404


def test_list_notes_with_key(example_client):
    client, mock_collection, _ = example_client
    mock_query = MagicMock()
    mock_collection.where.return_value.limit.return_value = mock_query
    mock_query.stream.return_value = []

    response = client.get("/api/notes?key=alice-test-key", follow_redirects=True)
    assert response.status_code == 200
    data = response.get_json()
    assert data["notes"] == []


def test_create_note(example_client):
    client, mock_collection, _ = example_client
    mock_doc = MagicMock()
    mock_doc.id = "note-1"
    mock_collection.document.return_value = mock_doc

    mock_query = MagicMock()
    mock_collection.where.return_value.limit.return_value = mock_query
    mock_query.stream.return_value = []

    response = client.post(
        "/api/notes?key=alice-test-key",
        json={"text": "Hello pytest"},
    )
    assert response.status_code == 201
    mock_doc.set.assert_called_once()
    data = response.get_json()
    assert data["note"]["text"] == "Hello pytest"
