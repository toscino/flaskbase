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
        pinned = [n for n in notes if n.get("pinned")]
        rest = [n for n in notes if not n.get("pinned")]
        pinned.sort(key=lambda n: n.get("created_at") or "", reverse=True)
        rest.sort(key=lambda n: n.get("created_at") or "", reverse=True)
        return pinned + rest

    def _get_owned_doc(self, user_id: str, note_id: str):
        """Return document snapshot if owned by user, else raise ValueError."""
        doc = self.collection.document(note_id).get()
        if not doc.exists:
            raise ValueError("Note not found")
        data = doc.to_dict() or {}
        if data.get("user_id") != user_id:
            raise ValueError("Note not found")
        return doc

    def delete_note(self, user_id: str, note_id: str) -> None:
        """Delete a note owned by the user."""
        doc = self._get_owned_doc(user_id, note_id)
        doc.reference.delete()

    def set_pinned(self, user_id: str, note_id: str, pinned: bool) -> dict[str, Any]:
        """Pin or unpin a note."""
        doc = self._get_owned_doc(user_id, note_id)
        doc.reference.update({"pinned": pinned})
        data = doc.to_dict() or {}
        data["pinned"] = pinned
        data["id"] = doc.id
        return data

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
            "pinned": False,
        }
        doc_ref.set(payload)
        payload["id"] = doc_ref.id
        return payload
