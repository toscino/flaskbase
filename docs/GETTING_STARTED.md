# Getting started (step by step)

This guide assumes **Windows** and that you open terminals in **Cursor** (Terminal → New Terminal). Mac/Linux notes appear where commands differ.

You will:

1. Set up Python and this project on your machine  
2. Set up Google Cloud (Firestore, App Engine, billing)  
3. Run the example app in your browser  
4. (Optional) Deploy to App Engine  

Before first App Engine deploy: publish a GitHub Release wheel — [Step 5](#step-5-publish-flask-base-github-release).

---

## Before you begin

| You need | Notes |
|----------|--------|
| This repo on your PC | e.g. `C:\Users\ianmb\Code\FlaskBase` |
| Python 3.10+ | Check with `python --version` |
| A Google account | For GCP (free tier is enough for testing) |
| ~30 minutes | First time through |

---

## Step 1: Set up your environment (local)

### 1.1 Check Python

In a terminal:

```powershell
python --version
```

You want **3.10, 3.11, or 3.12**. If `python` is not found, install from [python.org](https://www.python.org/downloads/) and tick **“Add python.exe to PATH”**.

### 1.2 Go to the project folder

```powershell
cd C:\Users\ianmb\Code\FlaskBase
```

Use your actual path if it is different.

### 1.3 Create a virtual environment (venv)

A venv keeps this project’s packages separate from everything else.

```powershell
python -m venv .venv
```

Activate it (you must do this in **each new terminal**):

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the start of the prompt.

Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 1.4 Install project dependencies

With `(.venv)` active and your folder at the **repo root** (`FlaskBase`, not `example`):

```powershell
pip install --upgrade pip
pip install -r requirements-dev.txt
```

This installs:

- `flask-base` (editable, from the `flask_base/` folder)  
- `pytest`  
- `gunicorn`  

Check the install:

```powershell
python -c "from flask_base import FlaskApp; print('OK')"
```

You should see `OK`.

### 1.5 Point Cursor at the venv (recommended)

This repo includes [`.vscode/settings.json`](../.vscode/settings.json) so new terminals use `.venv` automatically.

If the status bar still shows the wrong Python:

1. `Ctrl+Shift+P` → **Python: Select Interpreter**  
2. Choose `.venv\Scripts\python.exe`

### 1.6 Create your `.env` file

The example app reads secrets from `example\.env`.

```powershell
cd example
copy .env.example .env
```

Open `example\.env` in Cursor and edit it.

#### Generate random secrets

In a terminal (venv active), run **twice** to get two different values:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

Use one output for `FLASK_SECRET` and one for `ADMIN_KEY`.

#### Fill in `.env` (local-only values)

| Variable | What to put |
|----------|-------------|
| `GOOGLE_CLOUD_PROJECT` | Leave as placeholder for now — you will set this in Step 2 |
| `FLASK_SECRET` | First random string from above |
| `ADMIN_KEY` | Second random string from above |
| `FLASK_BASE_KEY_PREFIX` | Keep `EXAMPLE_KEY_` unless you know you need to change it |
| `EXAMPLE_KEY_ALICE` | Keep `alice-secret:view` for testing (means: URL key is `alice-secret`) |
| `EXAMPLE_KEY_BOB` | Optional second user |

Example (do **not** copy these secrets — use your own):

```env
GOOGLE_CLOUD_PROJECT=my-flaskbase-test-123
FLASK_SECRET=your-random-string-here
ADMIN_KEY=another-random-string-here
FLASK_BASE_KEY_PREFIX=EXAMPLE_KEY_
EXAMPLE_KEY_ALICE=alice-secret:view
```

Save the file. **Never commit `.env`** — it is already in `.gitignore`.

### 1.7 Step 1 checklist

- [ ] `(.venv)` shows in the terminal  
- [ ] `python -c "from flask_base import FlaskApp"` works  
- [ ] `example\.env` exists with your own `FLASK_SECRET` and `ADMIN_KEY`  

You can run the app **without** GCP for a quick smoke test (home page may work; Notes needs Firestore from Step 2).

---

## Step 2: Set up Google Cloud

You need a GCP project so the example app can use **Firestore** (the Notes feature) and, if you deploy, **App Engine**.

**Do these in order:** billing → **App Engine** (2.5) → **Firestore** (2.6). Creating Firestore before App Engine can break deploy on a new project.

### 2.1 Install the Google Cloud CLI (`gcloud`)

1. Download: [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install)  
2. Run the installer (defaults are fine).  
3. Close and reopen Cursor’s terminal so `gcloud` is on your PATH.

Verify:

```powershell
gcloud --version
```

### 2.2 Sign in to Google Cloud

```powershell
gcloud auth login
```

A browser window opens — sign in with the Google account you use for GCP.

### 2.3 Create a new GCP project (Console — easiest)

1. Open [Google Cloud Console](https://console.cloud.google.com/)  
2. Top bar → project dropdown → **New project**  
3. Name it something like `flaskbase-test`  
4. Note the **Project ID** (often similar to the name, e.g. `flaskbase-test-123456`) — not the display name  

Put that **Project ID** in `example\.env` (this is what the app uses):

```env
GOOGLE_CLOUD_PROJECT=flaskbase-test-123456
```

(Replace with your real project ID.)

**For `gcloud` CLI commands:** set the active project once (use the same ID as in `.env`). The example app also does this automatically when you `python app.py --run`.

```powershell
gcloud config set project flaskbase-test-123456
```

### 2.4 Billing (required)

GCP needs a billing account linked to the project before App Engine and Firestore, even if you stay within free quotas.

1. Console → **Billing** → link an account  
2. Set a [budget alert](https://cloud.google.com/billing/docs/how-to/budgets) if you want peace of mind  

### 2.5 Initialize App Engine (before Firestore)

A GCP **project** is not the same as an **App Engine app**. Do this **before** Firestore (Step 2.6).

**Region:** App Engine uses `us-central` (not `us-central1`). Firestore in Step 2.6 uses `us-central1` — they pair for US Central. You cannot change the App Engine region later.

Confirm project (must match `GOOGLE_CLOUD_PROJECT` in `example\.env`):

```powershell
gcloud config get-value project
gcloud services enable appengine.googleapis.com
gcloud app create --region=us-central
```

Confirm App Engine exists:

```powershell
gcloud app describe
```

If that prints app metadata (not an error), continue to Firestore.

### 2.6 Enable Firestore

**Prefer the Console (recommended).** The UI makes you pick **Native mode** explicitly. This app uses the Firestore Native API (Notes will break on Datastore mode).

**Option A — Console (recommended)**

1. Open [Firestore](https://console.cloud.google.com/firestore) and select your project  
2. **Create database** (if prompted)  
3. Choose **Firestore Native mode** — not “Datastore mode”  
4. Pick **us-central1** (pairs with App Engine `us-central`)  
5. Start in **test mode** for learning (tighten rules before production)  

Skip Option B if you already created the database here.

**Option B — Command line (easy to get wrong)**

Running only:

```powershell
gcloud services enable firestore.googleapis.com
```

can **auto-create** a `(default)` database for you. On new projects that database is sometimes **Datastore mode**, which this app cannot use. If that happens, delete the database in the Console and recreate via **Option A**, or wait for the cooldown and run the `create` command below with `--type=firestore-native`.

Safer CLI flow — enable the API, then create Native explicitly:

```powershell
gcloud config get-value project
gcloud services enable firestore.googleapis.com
gcloud firestore databases create --location=us-central1 --type=firestore-native
gcloud firestore databases list
```

After `create`, check the `type` column — it must say `FIRESTORE_NATIVE`, not `DATASTORE_MODE`.

If you see **already exists**, check the mode before skipping:

```powershell
gcloud firestore databases list
```

`type` must be `FIRESTORE_NATIVE`. If it says `DATASTORE_MODE`, delete `(default)` in the Console, wait a few minutes (Google holds the name during delete), then use **Option A** or run `create` again with `--type=firestore-native`.

If you see **Database ID '(default)' is not available** / retry in N seconds, the old database is still being removed — wait, then create again.

### 2.7 Let your PC access GCP (local development)

For Firestore on your machine, run:

```powershell
gcloud auth application-default login
```

Sign in when the browser opens. This stores credentials your Python code uses locally (separate from `gcloud auth login`).

### 2.8 Step 2 checklist

- [ ] `example\.env` has your real `GOOGLE_CLOUD_PROJECT`  
- [ ] Billing linked to the project  
- [ ] `gcloud app describe` succeeds (App Engine initialized **before** Firestore)  
- [ ] Firestore database exists (**Native** mode, `us-central1` — verify with `gcloud firestore databases list`)  
- [ ] `gcloud auth application-default login` completed  
- [ ] After one `python app.py --run`, `gcloud config get-value project` matches (flask-base sets it for you)  

---

## Step 3: Run the example app locally

### 3.1 Start the server

```powershell
cd C:\Users\ianmb\Code\FlaskBase\example
```

(Adjust path if needed. Venv should still be active — if not, activate from repo root first.)

```powershell
python app.py --run
```

You should see checks pass and URLs printed, for example:

```text
Alice: http://127.0.0.1:8080/?key=alice-secret
Admin: http://127.0.0.1:8080/admin?key=...
```

### 3.2 Open the app in your browser

Click or paste the **Alice** link (or add `?key=alice-secret` to the home URL if you changed the key in `.env`).

You should see the **Home** page and your signed-in name.

### 3.3 Try Notes (Firestore)

1. Click **Go to Notes** or open `http://127.0.0.1:8080/notes?key=alice-secret`  
2. Type a note and click **Add**  

If it works, a document appears in Firestore collection `example_notes` (visible in Cloud Console → Firestore).

### 3.4 Stop the server

In the terminal: `Ctrl+C`.

### 3.5 Run tests (optional)

From the **repo root**:

```powershell
cd C:\Users\ianmb\Code\FlaskBase
python -m pytest tests/ -v
```

---

## Step 4: Deploy to App Engine

Complete [Step 2.5](#25-initialize-app-engine-before-firestore) first. If deploy says the project has no App Engine application, you skipped that step or created Firestore first (see troubleshooting).

**Before the first deploy:** publish `flask-base` as a [GitHub Release](https://github.com/toscino/flaskbase/releases) wheel (see [Step 5](#step-5-publish-flask-base-github-release)). App Engine installs it from the pinned URL in `example/requirements.txt`, not from your local editable install.

### Deploy config (soft overview)

Three files, three jobs — easy to mix up at first:

| File | Used when | In git? |
|------|-----------|---------|
| `example\.env` | `python app.py --run` on your PC | No (gitignored) |
| `example\app.yaml` | Example / template only; **not** local dev | Yes (placeholders are fine) |
| `example\app.production.yaml` | `python app.py --deploy` to App Engine | No (you create this) |

**`app.yaml` is not your dev config.** Local dev uses `.env` only. The committed `app.yaml` is there so you can see what a deploy file looks like (runtime, scaling, env var names). Obvious placeholder secrets like `replace-with-admin-key` are fine — you are not meant to put real production secrets in it.

**To upload to the cloud**, create `app.production.yaml` once by copying the committed template (same structure as `app.yaml`):

```powershell
cd example
copy app.yaml app.production.yaml
```

Edit `app.production.yaml` with **production** values (new random secrets — not the same ones as `.env`). That file stays on your machine; git ignores it.

App Engine never reads `.env` on the server. Use the **same variable names** as `.env`, but **different values** for secrets:

| Variable | Local (`.env`) | Cloud (`app.production.yaml`) |
|----------|----------------|----------------------------------|
| `GOOGLE_CLOUD_PROJECT` | Your project ID | Usually the same ID |
| `FLASK_SECRET` | Your dev secret | New random string |
| `ADMIN_KEY` | Your dev admin key | New admin key |
| `FLASK_BASE_KEY_PREFIX` | e.g. `EXAMPLE_KEY_` | Usually the same |
| `EXAMPLE_KEY_*` | e.g. `alice-secret` | New URL keys (e.g. `prod-alice-secret`) |

### Deploy

From `example\` (with `app.production.yaml` in place):

```powershell
python app.py --deploy
```

Deploy automatically picks `app.production.yaml` when that file exists. Otherwise it falls back to `app.yaml`.

Visit `https://YOUR_PROJECT_ID.appspot.com/?key=your-production-user-secret` (the secret from `app.production.yaml`, not local `.env`).

### Step 4 checklist

- [ ] GitHub Release `v0.2.0` exists with wheel asset (Step 5)  
- [ ] `example/requirements.txt` pins that Release wheel URL  
- [ ] `app.production.yaml` exists with production secrets  
- [ ] Step 2.5 App Engine initialized  
- [ ] Deploy succeeded  
- [ ] Home and Notes work on the live URL with `?key=`

### Build your own app

Copy patterns from `example/`, read [QUICKSTART.md](../flask_base/QUICKSTART.md).

---

## Step 5: Publish flask-base (GitHub Release)

Library repo: [github.com/toscino/flaskbase](https://github.com/toscino/flaskbase). Production apps install a **pinned wheel URL** from GitHub Releases (not PyPI). Local dev still uses editable install from `requirements-dev.txt`.

### First release (manual or CI)

**Option A — tag push (recommended after CI is on `main`):**

```powershell
cd flask_base
pip install build
python -m build
cd ..
git tag v0.2.0
git push origin v0.2.0
```

GitHub Actions ([`.github/workflows/publish.yml`](../.github/workflows/publish.yml)) builds the wheel and attaches it to the Release.

**Option B — manual upload:** GitHub → Releases → **Create release** → tag `v0.2.0` → upload `flask_base/dist/flask_base-0.2.0-py3-none-any.whl`.

### Pin the wheel in your app

In `example/requirements.txt` (already set for this repo):

```text
flask-base @ https://github.com/toscino/flaskbase/releases/download/v0.2.0/flask_base-0.2.0-py3-none-any.whl
gunicorn>=21.0.0
```

Bump the URL when you tag `v0.2.1`, etc. Same URL works for every GCP project — no per-project registry.

### Optional: private Artifact Registry

Use GCP Artifact Registry only if the library must stay private. See historical notes in git history or add `gcloud artifacts repositories create` per [Google Cloud docs](https://cloud.google.com/artifact-registry/docs/python/store-python).

---

## Troubleshooting

### `ModuleNotFoundError: flask_base`

**Local:** Activate venv: `.\.venv\Scripts\Activate.ps1` — from repo root: `pip install -r requirements-dev.txt`  

**App Engine (502 / nginx / upstream connect error):** Check logs (`gcloud app logs read -s default --limit=20`). If you see `No module named 'flask_base'`, ensure `example/requirements.txt` includes the GitHub Release wheel URL and that Release exists on GitHub before redeploying.

### `../flask_base is not a valid editable requirement`

You ran `pip install -r example\requirements.txt` from the **wrong folder**. Use `requirements-dev.txt` from the **repo root** (Step 1.4).

### `FLASK_SECRET` / `ADMIN_KEY` errors

- File must be `example\.env` (not only `.env` in the root)  
- Run the app from the `example` folder so `.env` is found  

### Port 8080 already in use

Stop the other app using 8080, or in `.env` set `PORT=8081` and use that port in the browser.

### 404 on pages in the browser

- Add `?key=alice-secret` (or whatever secret you set in `EXAMPLE_KEY_ALICE` **before** the colon)  
- `EXAMPLE_KEY_ALICE=alice-secret:view` → use `?key=alice-secret`  

### Firestore / permission errors on Notes

- `GOOGLE_CLOUD_PROJECT` in `.env` matches `gcloud config get-value project`  
- Ran `gcloud auth application-default login`  
- Firestore database created in that project  
- Billing enabled on the project  

### “Firestore API is not available for Firestore in Datastore Mode”

The `(default)` database is **Datastore mode**, not **Native**. Recreate it via [Step 2.6 Option A](#26-enable-firestore) (Console). You cannot change mode in place.

### “Database ID '(default)' is not available”

You deleted `(default)` recently. Wait a few minutes, then create again (Console or CLI with `--type=firestore-native`).

### `gcloud` not found

Restart the terminal after installing the Cloud SDK, or reinstall and ensure “Add to PATH” is checked.

### Deploy: project does not contain an App Engine application

Run [Step 2.5](#25-initialize-app-engine-before-firestore) with `--region=us-central` (not `us-central1`).

### `app create` says already exists, but `app deploy` / `app describe` say no App Engine app

You likely created **Firestore before App Engine**, or used `--region=us-central1` instead of `us-central`. See [Fix a stuck project](#fix-a-stuck-project-throwaway-db) below.

### Fix a stuck project (throwaway DB)

Only if the Firestore database has **no data you need**. Replace `flaskbase-test` with your project ID.

**1. Confirm project**

```powershell
gcloud config set project flaskbase-test
gcloud config get-value project
```

**2. Delete the Firestore `(default)` database**

```powershell
gcloud firestore databases delete --database="(default)" --project=flaskbase-test
```

Type `Y` when prompted. Or delete in [Firestore Console](https://console.cloud.google.com/firestore).

**3. Create App Engine** (use `us-central`, not `us-central1`)

```powershell
gcloud app create --region=us-central
gcloud app describe
```

`app describe` must print JSON/metadata, not an error.

If `gcloud app create` fails with **internal error [13]**, wait a few minutes and retry, or use [App Engine Console](https://console.cloud.google.com/appengine?project=flaskbase-test) → **Create Application** → region **us-central**.

**4. Recreate Firestore**

```powershell
gcloud firestore databases create --location=us-central1
gcloud firestore databases list
```

**5. Local credentials** (if not done recently)

```powershell
gcloud auth application-default login
```

**6. Deploy**

```powershell
cd example
python app.py --deploy
```

---

## Quick reference (daily use)

```powershell
cd C:\Users\ianmb\Code\FlaskBase
.\.venv\Scripts\Activate.ps1
cd example
python app.py --run
```

Browser: use the printed URL with `?key=...`.
