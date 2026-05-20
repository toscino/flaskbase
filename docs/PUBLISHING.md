# Publishing flask-base (GitHub Release)

Apps install **flask-base** as a pinned wheel from [GitHub Releases](https://github.com/toscino/flaskbase/releases), not from PyPI. The example app’s `requirements.txt` is the reference.

## Pin a version in your app

```text
flask-base @ https://github.com/toscino/flaskbase/releases/download/v0.3.0/flask_base-0.3.0-py3-none-any.whl
gunicorn>=21.0.0
```

Use the same file for **local runs** and **App Engine** so behavior matches. Bump the URL when you publish `v0.2.1`, etc.

## Publish a new release

### Option A — tag push (CI)

From repo root, after merging changes to `flask_base/`:

```powershell
cd flask_base
pip install build
python -m build
cd ..
git tag v0.2.0
git push origin v0.2.0
```

[`.github/workflows/publish.yml`](../.github/workflows/publish.yml) builds the wheel and attaches it to the GitHub Release.

### Option B — manual upload

1. `cd flask_base` → `python -m build`
2. GitHub → **Releases** → **Create release** → tag `v0.2.0`
3. Upload `flask_base/dist/flask_base-0.2.0-py3-none-any.whl`

Then update every app’s `requirements.txt` to the new URL.

## After you publish

1. Update `example/requirements.txt` (and any other apps) with the new wheel URL.
2. Redeploy App Engine apps so Cloud Build picks up the new pin.
3. See [DEVELOPMENT.md](DEVELOPMENT.md) if you were using an editable local install while hacking the library.

## Optional: private Artifact Registry

Use [Google Artifact Registry](https://cloud.google.com/artifact-registry/docs/python/store-python) only if the package must stay private. The example repo is set up for public GitHub Release wheels.

## Troubleshooting deploy installs

If App Engine logs show `No module named 'flask_base'`:

- `requirements.txt` must include the `flask-base @ https://...whl` line.
- The tag and wheel must exist on GitHub (open the Release URL in a browser).
- Redeploy after fixing `requirements.txt`.
