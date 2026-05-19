"""Minimal Firestore notes service for the example app."""

from datetime import datetime, timezone
from typing import Any


class NotesService:
    """List and create notes in Firestore."""

    COLLECTION = "example_notes"

    def __init__(self, app_manager: Any) -> None:
        self.logger = app_manager.logger
        self.db = app_manager.db
        self.collection = self.db.collection(self.COLLECTION)

    def list_notes(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Return recent notes for the authenticated user."""
        query = self.collection.where("user_id", "==", user_id).limit(limit)
        notes = []
        for doc in query.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            notes.append(data)
        notes.sort(key=lambda n: n.get("created_at") or "", reverse=True)
        return notes

    def create_note(self, user_id: str, text: str) -> dict[str, Any]:
        """Create a note document."""
        text = text.strip()
        if not text:
            raise ValueError("Note text is required")

        now = datetime.now(timezone.utc)
        doc_ref = self.collection.document()
        payload = {
            "user_id": user_id,
            "text": text,
            "created_at": now,
        }
        doc_ref.set(payload)
        payload["id"] = doc_ref.id
        return payload
