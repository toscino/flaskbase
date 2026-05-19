# Google Cloud setup (Phase 2)

This guide publishes `flask-base` to a private GitHub repo and Google Artifact Registry, then deploys the `example/` app to App Engine.

## Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
- [GitHub CLI](https://cli.github.com/) (`gh`) — optional but convenient
- A GCP billing account and a **new** GCP project for testing

## 1. Private GitHub repository

From the repository root (after `git init`):

```bash
gh repo create flask-base --private --source=. --remote=origin
git push -u origin main
```

Protect `main` in GitHub settings. Publish releases from **git tags** (e.g. `v0.2.0`).

## 2. Enable GCP APIs

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable appengine.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud app create --region=us-central
```

Create a Firestore database in **Native** mode if prompted (Console or `gcloud firestore databases create`).

## 3. Artifact Registry (Python)

```bash
gcloud artifacts repositories create flask-base-python \
  --repository-format=python \
  --location=us-central1 \
  --description="flask-base wheels"
```

## 4. Build and publish a wheel (one-off)

From your machine (authenticated with `gcloud auth application-default login`):

```bash
cd flask_base
pip install build twine keyrings.google-artifactregistry-auth
python -m build
```

Upload (replace `PROJECT_ID` and region):

```bash
twine upload --repository-url https://us-central1-python.pkg.dev/PROJECT_ID/flask-base-python/ dist/*
```

Or use the GitHub Actions workflow in [`.github/workflows/publish.yml`](../.github/workflows/publish.yml) after configuring Workload Identity Federation (see [Google's guide](https://github.com/google-github-actions/auth)).

## 5. Consume the package in an app

`example/requirements.txt` (production):

```text
--extra-index-url https://us-central1-python.pkg.dev/PROJECT_ID/flask-base-python/simple/
flask-base==0.2.0
gunicorn>=21.0.0
```

Grant the **App Engine default service account** the role **Artifact Registry Reader**:

```bash
PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format='value(projectNumber)')
gcloud artifacts repositories add-iam-policy-binding flask-base-python \
  --location=us-central1 \
  --member="serviceAccount:${PROJECT_NUMBER}@appspot.gserviceaccount.com" \
  --role="roles/artifactregistry.reader"
```

Local pip with the same index:

```bash
pip install keyrings.google-artifactregistry-auth
pip install flask-base==0.2.0 --extra-index-url https://us-central1-python.pkg.dev/PROJECT_ID/flask-base-python/simple/
```

## 6. Deploy the example app

1. Copy `example/.env.example` to `example/.env` and set secrets.
2. Update `example/app.yaml` with the same env vars (no secrets in git for real projects — use Secret Manager later).
3. Deploy from the example directory:

```bash
cd example
gcloud config set project YOUR_PROJECT_ID
gcloud app deploy app.yaml
```

Or: `python app.py --deploy` (uses `GOOGLE_CLOUD_PROJECT` from `.env`).

4. Visit `https://YOUR_PROJECT_ID.appspot.com/?key=your-user-secret`

## 7. Verify

- Home and Notes pages load when authenticated via `?key=`
- `POST /api/notes` creates a document in Firestore collection `example_notes`
- `GET /api/notes` returns your notes

## Troubleshooting

| Issue | Check |
|-------|--------|
| `FLASK_SECRET` / `ADMIN_KEY` errors | Set in `.env` locally or `app.yaml` on GAE |
| 404 on pages | Valid `?key=` matching `FLASK_BASE_KEY_PREFIX` env vars |
| Firestore permission denied | Enable Firestore API; App Engine service account has datastore access |
| pip cannot find `flask-base` on deploy | Extra-index URL, AR reader role, package version published |
