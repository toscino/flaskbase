"""Example app demonstrating flask-base v0.4.0 LLM features (app_manager.llm)."""

from flask_base import FlaskApp

from services.llm_service import LLMService

app_manager = FlaskApp(app_name="FlaskBase LLM Example", demo_user="demo")
app_manager.limiter.default_limits = ["200 per hour", "60 per minute"]
app = app_manager.app

llm_service = LLMService(app_manager)

app_manager.page("landing.html", root=True)
app_manager.page("ask.html", auth=True)


@app_manager.route("/api/ask", methods=["POST"], auth=True, limit="20 per minute")
def ask_llm():
    """Generate unstructured text via app_manager.llm.generate_text()."""
    try:
        data = app_manager.get_json()
    except ValueError as exc:
        return app_manager.jsonify({"error": str(exc)}), 400

    prompt = (data.get("prompt") or "").strip()
    system_instruction = (data.get("system_instruction") or "").strip() or None
    if not prompt:
        return app_manager.jsonify({"error": "prompt is required"}), 400

    try:
        answer = llm_service.ask(prompt, system_instruction=system_instruction)
    except Exception as exc:
        return app_manager.jsonify({"error": str(exc)}), 502

    return app_manager.jsonify({"text": answer})


@app_manager.route("/api/summarize", methods=["POST"], auth=True, limit="20 per minute")
def summarize_text():
    """Generate structured JSON validated by Pydantic via app_manager.llm.generate_json()."""
    try:
        data = app_manager.get_json()
    except ValueError as exc:
        return app_manager.jsonify({"error": str(exc)}), 400

    text = (data.get("text") or "").strip()
    if not text:
        return app_manager.jsonify({"error": "text is required"}), 400

    try:
        result = llm_service.summarize(text)
    except Exception as exc:
        return app_manager.jsonify({"error": str(exc)}), 502

    return app_manager.jsonify({"result": result.model_dump()})


if __name__ == "__main__":
    app_manager.run()
