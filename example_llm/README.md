# LLM Example App

Minimal runnable demo showcasing `flask-base` v0.4.0's optional Google Gen AI (`app_manager.llm`) integration:

- **`POST /api/ask`** — unstructured text generation via `app_manager.llm.generate_text()`
- **`POST /api/summarize`** — structured JSON validated with Pydantic via `app_manager.llm.generate_json()`

## Prerequisites

- Python 3.10+
- GCP project with Vertex AI API enabled and Application Default Credentials (`gcloud auth application-default login`)

## Quick run

From this folder (`example_llm/`) with your venv active:

```powershell
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your GOOGLE_CLOUD_PROJECT and secrets
python app.py --run
```

Then open `http://127.0.0.1:8080/?key=alice-secret` and click **Open LLM Playground** (`/ask`).

> **Developing locally in this monorepo?** Install the editable package with LLM extras from repo root instead:
> ```powershell
> pip install -e "./flask_base[llm]"
> ```

## Deploy to App Engine

```powershell
copy app.yaml app.production.yaml
# Edit app.production.yaml with your real project ID and secrets
python app.py --deploy
```
