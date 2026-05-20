# flask-base documentation

Guides for **using and developing the library**. To run the demo app (Python, `gcloud`, deploy), use **[example/GETTING_STARTED.md](../example/GETTING_STARTED.md)** instead.

## Run the example app

| Doc | Purpose |
|-----|---------|
| [example/README.md](../example/README.md) | Entry point |
| [example/GETTING_STARTED.md](../example/GETTING_STARTED.md) | Full setup: venv, `.env`, GCP, local run, App Engine deploy |

## Use flask-base in your project

| Doc | Purpose |
|-----|---------|
| [flask_base/QUICKSTART.md](../flask_base/QUICKSTART.md) | API: `FlaskApp`, auth keys, pages, routes, deploy helpers |
| [CONFIG_GUIDE.md](CONFIG_GUIDE.md) | Environment variables and key prefix |
| [API_CONTRACTS.md](API_CONTRACTS.md) | API shapes and conventions |

## Install the package

| Doc | Purpose |
|-----|---------|
| [PUBLISHING.md](PUBLISHING.md) | GitHub Release wheels, pinning `requirements.txt`, CI |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Editable install in this monorepo, local vs release wheel |

## Design and architecture

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | How the library fits together |
| [DESIGN_GUIDE.md](DESIGN_GUIDE.md) | Design notes |
| [FRONTEND_COMPONENTS.md](FRONTEND_COMPONENTS.md) | Templates and UI |
| [PORTABILITY.md](PORTABILITY.md) | Porting to other stacks |
| [AI_AGENT_GUIDE.md](AI_AGENT_GUIDE.md) | Notes for AI-assisted development |

## GCP

Example-specific `gcloud` / Firestore / App Engine steps are in [example/GETTING_STARTED.md](../example/GETTING_STARTED.md) Step 2. [GCLOUD_SETUP.md](GCLOUD_SETUP.md) is a short pointer.
