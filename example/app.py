"""Example app demonstrating flask-base: auth, pages, API, and Firestore."""

from flask_base import FlaskApp

from services.notes_service import NotesService

app_manager = FlaskApp(app_name="FlaskBase Example", demo_user="demo")
app_manager.limiter.default_limits = ["200 per hour", "60 per minute"]
app = app_manager.app

notes_service = NotesService(app_manager)

app_manager.page("landing.html", root=True)
app_manager.page("home.html", auth=True)
app_manager.page("notes.html", auth=True)
app_manager.page("patterns.html", auth=True)


@app_manager.route("/api/notes", methods=["GET"], auth=True, limit="60 per minute")
def list_notes():
    """List notes for the current user."""
    notes = notes_service.list_notes(app_manager.current_user)
    return app_manager.jsonify({"notes": notes})


@app_manager.route("/api/notes", methods=["POST"], auth=True, limit="30 per minute")
def create_note():
    """Create a note for the current user."""
    try:
        data = app_manager.get_json()
    except ValueError as exc:
        return app_manager.jsonify({"error": str(exc)}), 400

    text = data.get("text", "")
    try:
        note = notes_service.create_note(app_manager.current_user, text)
    except ValueError as exc:
        return app_manager.jsonify({"error": str(exc)}), 400

    return app_manager.jsonify({"note": note}), 201


@app_manager.route("/api/notes/<note_id>", methods=["DELETE"], auth=True, limit="30 per minute")
def delete_note(note_id: str):
    """Delete a note for the current user."""
    try:
        notes_service.delete_note(app_manager.current_user, note_id)
    except ValueError as exc:
        return app_manager.jsonify({"error": str(exc)}), 404
    return app_manager.jsonify({"ok": True})


@app_manager.route("/api/notes/<note_id>", methods=["PATCH"], auth=True, limit="30 per minute")
def patch_note(note_id: str):
    """Update note fields (e.g. pinned)."""
    try:
        data = app_manager.get_json()
    except ValueError as exc:
        return app_manager.jsonify({"error": str(exc)}), 400

    if "pinned" not in data:
        return app_manager.jsonify({"error": "No supported fields to update"}), 400

    try:
        note = notes_service.set_pinned(
            app_manager.current_user, note_id, bool(data["pinned"])
        )
    except ValueError as exc:
        return app_manager.jsonify({"error": str(exc)}), 404

    return app_manager.jsonify({"note": note})


if __name__ == "__main__":
    app_manager.run()
