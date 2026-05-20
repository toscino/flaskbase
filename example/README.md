# Example app

Runnable demo: [flask-base](https://github.com/toscino/flaskbase) auth, pages, Firestore notes, App Engine deploy.

## Getting started

**[GETTING_STARTED.md](GETTING_STARTED.md)** — install Python deps, set up `gcloud` and GCP, configure `.env`, run locally, deploy.

This guide is **only** about running this app. For the flask-base library (API, publishing wheels, developing the package), see **[docs/README.md](../docs/README.md)**.

## Quick run (GCP already set up)

From this folder with venv active (see GETTING_STARTED for venv setup):

```powershell
pip install -r requirements.txt
copy .env.example .env
# Edit .env
python app.py --run
```

Open `http://127.0.0.1:8080/` or `/?key=alice-secret`.

UI patterns (settings layout, tabs, messages): sign in, then open `/patterns`.

## Deploy

```powershell
copy app.yaml app.production.yaml
# Edit app.production.yaml — align FLASK_BASE_KEY_PREFIX with your EXAMPLE_KEY_* vars
python app.py --deploy
```

See [GETTING_STARTED.md](GETTING_STARTED.md) Step 4.
