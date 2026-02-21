# GreenPulse 🌿
A complete community plantation tracking web app built with Flask + SQLite for college project demonstration.

## 1) Folder Structure
```text
GREENHUB/
├── app.py
├── requirements.txt
├── Procfile
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── register.html
│   ├── login.html
│   ├── add_plantation.html
│   ├── records.html
│   ├── map.html
│   ├── dashboard.html
│   └── about.html
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── uploads/
│       └── .gitkeep
└── .gitignore
```

## 2) Database Schema
SQLite DB file: `greenpulse.db` (auto-created)

### `users`
- `id` (INTEGER, PK, AUTOINCREMENT)
- `username` (TEXT, UNIQUE, NOT NULL)
- `email` (TEXT, UNIQUE, NOT NULL)
- `password_hash` (TEXT, NOT NULL)
- `created_at` (TEXT, NOT NULL)

### `plantations`
- `id` (INTEGER, PK, AUTOINCREMENT)
- `user_id` (INTEGER, FK -> users.id)
- `tree_name` (TEXT, NOT NULL)
- `plantation_date` (TEXT, NOT NULL)
- `location_text` (TEXT, NOT NULL)
- `latitude` (REAL)
- `longitude` (REAL)
- `image_filename` (TEXT)
- `status` (TEXT default `Growing`)
- `created_at` (TEXT)

## 3) Full Flask Backend Code
- Main application is in `app.py`.
- Includes:
  - authentication (register/login/logout)
  - password hashing
  - SQLite CRUD
  - upload validation (`jpg`, `jpeg`, `png`)
  - dashboard stats + CO₂ estimate
  - map API (`/api/plantations`)

## 4) All HTML Templates
All required templates are in `templates/`:
- Home, Auth pages, Add Plantation, Records, Map, Dashboard, About
- Navbar automatically changes by login state

## 5) Full CSS with Animations
In `static/css/style.css`:
- nature theme + modern cards
- animated hero plant growth
- transitions for buttons/cards/forms
- responsive mobile/desktop layout

## 6) JavaScript (Location + UI)
In `static/js/main.js`:
- browser geolocation auto-fill (lat/lng)
- animated dashboard counters
- OpenStreetMap Leaflet map markers loaded from API

## 7) Local Run Steps (VS Code)
1. Open project folder in VS Code.
2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
4. Run app:
   ```bash
   python app.py
   ```
5. Open: `http://127.0.0.1:5000`

## 8) Deployment Guide (Render)
1. Push this project to GitHub.
2. Go to https://render.com and create account.
3. Click **New +** → **Web Service**.
4. Connect your GitHub repo.
5. Configure:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. Add Environment Variable (important key format rule):
   - Use a valid key name (letters, digits, `_`, `-`, or `.` only, and **must not start with a digit**).
   - Recommended key: `GREENPULSE_SECRET_KEY` (or `SECRET_KEY`) = any long random string.
   - Example valid keys: `GREENPULSE_SECRET_KEY`, `SECRET_KEY`, `FLASK_ENV`
   - Example invalid keys: `SECRET KEY`, `1SECRET_KEY`, `SECRET@KEY`
7. Click **Create Web Service**.
8. Render gives your live URL, e.g.:
   - `https://your-greenpulse-app.onrender.com`

> Live link is generated after deployment in your own Render account.
> You can copy values from `.env.example` and paste them into your deployment provider's environment variable panel.

## 9) Railway / PythonAnywhere (Alternative)
- Same app works using `requirements.txt` + `gunicorn app:app` on Railway.
- On PythonAnywhere, upload files, create web app with Flask, set WSGI entry to `app:app`.


## 10) Deployment Troubleshooting
- If provider shows: *"Environment variable keys must consist of alphabetic characters, digits, '_', '-', or '.', and must not start with a digit"*:
  - Rename keys to a valid format, e.g. `GREENPULSE_SECRET_KEY`.
  - Avoid spaces/special symbols in key names.
  - Keep only the **value** random, not the key format.
