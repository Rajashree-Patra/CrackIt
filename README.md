CrackIt — Exam Prep Platform
A focused, modern web app to help students discover exams, enroll in courses, and validate readiness with an eligibility mock test. Built for clarity, extensibility, and quick local development.

## Table of contents

- About
- Features
- Tech Stack
- Architecture & Workflow
- How It Works
- Installation
- Usage
- Project structure
- API (Endpoints)
- Development & Deployment
- Future enhancements
- Limitations

---

## About

- Purpose: Provide a lightweight platform for students to browse exam offerings, enroll in subjects, and validate their eligibility via a mock test.
- Audience: Students, educators, small coaching centers.
- Goals:
  - Simple developer experience for local setup
  - Clean templates and sensible defaults
  - Minimal, secure session handling and guard rails

---

## Features

- ✅ Student + Admin login (unified login page)
- ✅ Browse exams and view subject lists
- ✅ Enroll / drop subjects with notification feed
- ✅ Eligibility mock test gating key pages
- ✅ Admin dashboard with basic metrics & logs
- ✅ Simple DB migration seed via `/init_db` (dev convenience)

---

## Tech Stack

| Layer           | Technology                   |
| --------------- | ---------------------------- |
| Language        | Python 3.10+                 |
| Web framework   | Flask                        |
| Database        | PostgreSQL                   |
| ORM / DB driver | psycopg2                     |
| Frontend        | Jinja2 templates, static CSS |
| Dev / Tools     | dotenv, lucide icons (CDN)   |

Badges:

- Python, Flask, Postgres shown at top.

---

## Architecture & Workflow

A small, standard web-app architecture:
  Browser -->|HTTP| FlaskApp[Flask app (routes) ]
  FlaskApp -->|psycopg2| Postgres[(PostgreSQL DB)]
  FlaskApp -->|renders| Templates[Jinja2 templates]
  Templates -->|static assets| Static[(static/)]
  subgraph Auth
    FlaskApp --> Session[Session store (Flask session)]
  end


- The user interacts via browser; protected routes are guarded by `login_required` decorator.
- A server-side `check_eligibility` middleware redirects incomplete students to `/mock_test`.

---

## How It Works (high level)

1. Developer launches the Flask server (dev).
2. Users visit `/` and sign in / sign up.
3. Authenticated students see `/dashboard`. If `eligibility_test_score` is `NULL`, they get directed to `/mock_test`.
4. Student can `explore` exams, `enroll` in subjects, and view `timetable`.
5. Admin users have protected admin routes under `/admin/*`.

---

## Installation

Prereqs:

- Python 3.10+
- PostgreSQL running locally or accessible via `DATABASE_URL`

Quick start (Windows / cross-platform):

bash
# 1. clone
git clone https://github.com/your-org/CrackIt.git
cd CrackIt

# 2. create venv & install
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

# 3. create .env (example below)
cp .env.example .env
# edit .env to add DB credentials

# 4. run the app
python app.py
# then open http://127.0.0.1:5000


Example `.env.example` (create at repo root):

SECRET_KEY=replace_with_secure_value
Option A: full connection string
DATABASE_URL=postgresql://user:password@host:5432/crackit_db
# Option B: individual DB fields (if you don't use DATABASE_URL)
DB_HOST=localhost
DB_NAME=crackit_db
DB_USER=postgres
DB_PASS=postgres_password


---

## Usage

- Visit `http://127.0.0.1:5000` after starting the app.
- Create an account via `Sign up` and set `target exam`.
- If blocked from pages like `/dashboard`, complete `/mock_test` (eligibility).
- Admin login: select "Administrator" on the login page.

Common dev commands:

# Run tests (if added)
pytest

# Format
black .

# Lint
flake8

---

## Project structure

CrackIt/
├─ app.py                 # Main Flask app + routes
├─ requirements.txt
├─ schema.sql
├─ data.sql
├─ mock_data.py
├─ README.md
├─ templates/
│  ├─ base.html
│  ├─ index.html
│  ├─ unified_login.html
│  └─ ... other pages ...
└─ static/
   ├─ css/
   └─ images/

---

## API / Endpoints (summary)

| Path                       |   Method | Description                               |
| -------------------------- | -------: | ----------------------------------------- |
| `/`                        |      GET | Landing page (redirects if logged-in)     |
| `/login`                   | GET/POST | Unified login for student/admin           |
| `/signup`                  | GET/POST | Student registration                      |
| `/dashboard`               |      GET | Student dashboard (protected)             |
| `/explore`                 |      GET | Browse exams                              |
| `/exam/<int:exam_id>`      |      GET | Exam detail                               |
| `/enroll/<int:subject_id>` |      GET | Enroll student in subject                 |
| `/drop/<int:subject_id>`   |      GET | Drop subject                              |
| `/mock_test`               | GET/POST | Eligibility mock test                     |
| `/admin/*`                 |      GET | Admin views (admin-only)                  |
| `/init_db`                 |      GET | Initialize DB from schema/data (dev only) |

---

## Development & Deployment

- Development: built-in Flask server (`python app.py`) with `debug=True`.
- Production: run behind a WSGI server (Gunicorn) and a reverse proxy (NGINX).
- Example Gunicorn command:

# from project root
gunicorn -w 4 -b 0.0.0.0:8000 app:app

- Use environment variables for config (no hardcoded secrets).
- Database backups: use `pg_dump` regularly; store dumps securely.

---

## Future enhancements

- [ ] Convert enroll/drop to RESTful POST endpoints + CSRF protection
- [ ] Add automated tests (unit + integration)
- [ ] Containerize with Docker + docker-compose
- [ ] Add OAuth 2.0 / SSO for auth
- [ ] Add CI pipeline (GitHub Actions) with lint/test/build badges
- [ ] Replace raw SQL with lightweight ORM (SQLAlchemy) for portability

---

## Limitations

- Current session storage uses Flask's default signed cookies — not suitable for multi-instance scaling.
- Some state-changing actions are exposed via GET for simplicity (should be POST).
- No rate-limiting or brute-force protection on the login endpoint.
- The `init_db` route executes SQL files directly — only for local/dev use.

---
