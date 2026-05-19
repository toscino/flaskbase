# flask-base

A minimal Flask library for web apps with Firestore, key-based authentication, rate limiting, and Google App Engine deployment helpers.

## Repository layout

| Path | Purpose |
|------|---------|
| [`flask_base/`](flask_base/) | Installable Python package (`pip install`) |
| [`example/`](example/) | Starter app: auth pages, REST API, Firestore notes |
| [`docs/GCLOUD_SETUP.md`](docs/GCLOUD_SETUP.md) | GitHub, Artifact Registry, and App Engine setup |
| [`tests/`](tests/) | Package and example smoke tests |

## Quick start (local)

```bash
# Install the library in editable mode
pip install -e flask_base

# Run the example app
cd example
copy .env.example .env   # Windows; or cp on Unix
# Edit .env with your GCP project, FLASK_SECRET, ADMIN_KEY, and user keys
pip install -r requirements.txt
python app.py --run
```

Open the URL printed in the console (append `?key=your-user-secret` from `.env`).

## Install in a new project

**Development** (path dependency):

```text
-e /path/to/flask-base/flask_base
```

**Production** (private Artifact Registry — see [docs/GCLOUD_SETUP.md](docs/GCLOUD_SETUP.md)):

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
