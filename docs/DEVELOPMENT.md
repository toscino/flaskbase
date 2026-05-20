# Developing flask-base in this monorepo

For **running the example app only**, use [example/GETTING_STARTED.md](../example/GETTING_STARTED.md). This doc is for people changing code under `flask_base/`.

## Layout

| Path | Role |
|------|------|
| `flask_base/` | Library source (published as `flask-base` on GitHub Releases) |
| `example/` | Demo app; installs the Release wheel by default |
| `requirements-dev.txt` | Editable install (`-e flask_base`) + pytest + gunicorn |
| `tests/` | Smoke tests |

## Editable install (live library changes)

From repo root with venv active:

```powershell
pip install -r requirements-dev.txt
```

Edits under `flask_base/` apply on the next app restart. The example app will **not** match App Engine until you publish a new wheel.

## Match production (Release wheel)

From `example/`:

```powershell
pip install -r requirements.txt
```

Same pinned GitHub wheel as deploy. Use this to verify the example before you tag a release.

## Helper scripts (repo root, venv active)

```powershell
.\scripts\use-local-flask-base.ps1    # editable install
.\scripts\use-release-flask-base.ps1  # example/requirements.txt wheel
```

## Ship a library change

1. Develop with `requirements-dev.txt`.
2. Run tests: `pip install pytest` → `python -m pytest tests/ -v` from repo root.
3. Publish: [PUBLISHING.md](PUBLISHING.md) (tag + wheel).
4. Bump `example/requirements.txt` URL.
5. Redeploy the example if you want to verify cloud.

## `demo_user` in the example

`FlaskApp(..., demo_user="demo")` is only a fallback for `app_manager.current_user` when there is no session. It does **not** bypass `auth=True` on pages or APIs. See [QUICKSTART.md](../flask_base/QUICKSTART.md).
