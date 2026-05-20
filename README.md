# flask-base

**What this is:** A hobby project to make small Flask web apps less painful — auth, Firestore, App Engine deploy, and the usual glue — so I do not have to re‑remember every tool and boilerplate pattern each time I want something live quickly.

It was built heavily with AI help in early 2026. If that bothers future me (or you): that is intentional; please do not whine about it.

---

Minimal Flask toolkit for App Engine: key-based auth, Firestore helpers, rate limiting, deploy utilities.

## Run the example app

Clone the repo, open **`example/`**, and follow **[example/GETTING_STARTED.md](example/GETTING_STARTED.md)** — Python, `gcloud`, `.env`, local run, deploy.

On GitHub: browse to **`example/`** for [README](example/README.md) and the full guide.

## Quick start (already have Python + gcloud + GCP)

```powershell
git clone https://github.com/toscino/flaskbase.git
cd flaskbase
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r example/requirements.txt
cd example
copy .env.example .env
# Edit .env
python app.py --run
```

Use `/?key=alice-secret` (match `EXAMPLE_KEY_*` in `.env`). Troubleshooting: [example/GETTING_STARTED.md](example/GETTING_STARTED.md).

## flask-base library docs

**[docs/README.md](docs/README.md)** — using flask-base in your own apps, API ([QUICKSTART](flask_base/QUICKSTART.md)), [publishing wheels](docs/PUBLISHING.md), [monorepo development](docs/DEVELOPMENT.md), architecture guides.

## Repository layout

| Path | Purpose |
|------|---------|
| [`example/`](example/) | Runnable demo + getting started (GCP included) |
| [`flask_base/`](flask_base/) | Library source |
| [`docs/`](docs/) | Library documentation |
| [`tests/`](tests/) | Smoke tests |

## License

MIT — see [`flask_base/LICENSE`](flask_base/LICENSE).
