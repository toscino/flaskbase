# flask-base

A minimal Flask library for web apps with Firestore, key-based authentication, rate limiting, and Google App Engine deployment helpers.

## New here?

Follow **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** — step-by-step setup for:

1. **Environment** — Python, venv, Cursor, install, `.env`  
2. **Google Cloud** — `gcloud`, project, Firestore, App Engine, billing  
3. **Run the example app** — browser, Notes, tests  
4. **Deploy** — `app.production.yaml`, App Engine  
5. **Publish package** (optional) — GitHub, Artifact Registry  

## Repository layout

| Path | Purpose |
|------|---------|
| [`flask_base/`](flask_base/) | Installable Python package (`pip install`) |
| [`example/`](example/) | Starter app: auth pages, REST API, Firestore notes |
| [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) | Full setup: local, GCP, deploy, optional publishing |
| [`docs/GCLOUD_SETUP.md`](docs/GCLOUD_SETUP.md) | Redirect — content lives in GETTING_STARTED |
| [`tests/`](tests/) | Package and example smoke tests |

## Quick start (if you already know the steps)

```powershell
# Repo root, venv active
pip install -r requirements-dev.txt
cd example
copy .env.example .env
# Edit .env — see GETTING_STARTED.md
python app.py --run
```

Open the URL printed in the console (use `?key=` from `.env`, e.g. `alice-secret`).

## Install in a new project

**Development** (path dependency):

```text
-e /path/to/flask-base/flask_base
```

**Production** (private Artifact Registry — see [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) Step 5):

```text
--extra-index-url https://REGION-python.pkg.dev/PROJECT_ID/flask-base-python/simple/
flask-base==0.2.0
```

**Fallback:** copy the `flask_base/` folder into your project (not recommended long term).

## Minimal app

```python
from flask_base import FlaskApp

app_manager = FlaskApp("My App")
app_manager.page("home.html", auth=True, root=True)
app = app_manager.app

if __name__ == "__main__":
    app_manager.run()
```

See [`flask_base/QUICKSTART.md`](flask_base/QUICKSTART.md) for auth keys, services, and deployment.

## Deploy example to App Engine

```bash
cd example
gcloud config set project YOUR_PROJECT_ID
python app.py --deploy
```

Requires `app.yaml` env vars and Firestore API enabled in your GCP project.

## License

MIT — see [`flask_base/LICENSE`](flask_base/LICENSE).
