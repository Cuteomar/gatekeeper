# 🚪 GateKeeper — Role-Based Access Control System

A production-ready RBAC web application built with **Flask**, **bcrypt**, and **SQLAlchemy**. Features include user authentication, role/permission management, backend-level access enforcement, and full audit logging.

---

## 📋 Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Security Notes](#security-notes)
- [Learning Outcomes](#learning-outcomes)
- [Suggested Improvements](#suggested-improvements)
- [API Endpoint Reference](#api-endpoint-reference)
- [Project Structure](#project-structure)

---

## ✨ Features

| Feature | Description |
|---|---|
| **User Authentication** | Register, login, logout with session-based auth (Flask-Login) |
| **Password Security** | Bcrypt hashing (12 rounds), minimum 8-char passwords |
| **Role Management** | Create/edit roles, each with a set of granular permissions |
| **Permission Enforcement** | `@admin_required`, `@role_required()`, `@permission_required()` decorators |
| **Admin Dashboard** | User list, role assignment, user activation/deactivation |
| **Audit Logging** | Every login, logout, role change, and denied access is recorded with IP |
| **CSRF Protection** | WTForms CSRF tokens on all POST requests |
| **Dark UI** | Bootstrap 5 dark theme with responsive design |

---

## 🛠 Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.9+** | Runtime |
| **Flask 3.1** | Web framework |
| **Flask-SQLAlchemy** | ORM and database abstraction |
| **Flask-Login** | Session-based user authentication |
| **Flask-Bcrypt** | Password hashing (bcrypt, `log_rounds=12`) |
| **Flask-WTF / WTForms** | Form validation and CSRF protection |
| **Flask-Migrate / Alembic** | Database migration management |
| **SQLite** (dev) / **PostgreSQL** (prod) | Relational database |
| **Bootstrap 5.3** | Frontend UI (dark theme) |

---

## 📦 Installation

### Prerequisites

- Python 3.9 or later
- pip

### Step-by-step

```bash
# 1. Clone the repository
git clone https://github.com/Cuteomar/gatekeeper.git
cd gatekeeper

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it (Windows)
venv\Scripts\activate
#    (macOS / Linux)
# source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Seed the database
python seed.py

# 6. Run the server
flask run
#    or:   python run.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 🚀 Quick Start

After running `python seed.py`, three test users are created:

| Username | Password | Role      | Permissions |
|----------|----------|-----------|-------------|
| `admin`  | admin123 | **admin** | All permissions |
| `staff`  | staff123 | **staff** | `read:content`, `write:content` |
| `guest`  | guest123 | **guest** | `read:content` |

---

## 🌐 Deploy to Render (Free, Vercel-like)

GateKeeper is ready to deploy on **Render** — it creates a free PostgreSQL database and web service automatically.

### One-click deploy

1. Push the repo to GitHub (already done)
2. Go to **[dashboard.render.com](https://dashboard.render.com)**
3. Click **New → Blueprint** and connect your `gatekeeper` repo
4. Render reads `render.yaml` and sets up:
   - A **web service** with Gunicorn (2 workers)
   - A **free PostgreSQL database**
   - Auto-generated `SECRET_KEY`
5. Click **Apply** — deploy takes ~3 minutes
6. Once live, run the seed script once in the Render shell:
   ```bash
   python seed.py
   ```

Your app will be at: `https://gatekeeper.onrender.com`

### Alternative: Manual setup on Render

1. Create a **Web Service** → connect GitHub repo
2. Set **Build Command**: `pip install -r requirements.txt`
3. Set **Start Command**: `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2`
4. Add a **PostgreSQL database** (free tier) from the Render dashboard
5. Copy the database URL into an environment variable `DATABASE_URL`
6. Add a secret `SECRET_KEY` env var (any random string)
7. Deploy, then run `python seed.py` in the Render shell

### Other free options

| Platform | Setup | URL format |
|----------|-------|------------|
| **Railway** | Connect repo → auto-detects Flask | `gatekeeper.up.railway.app` |
| **PythonAnywhere** | Manual git pull, manual WSGI config | `yourusername.pythonanywhere.com` |
| **Fly.io** | `fly launch` CLI, auto Flask detection | `gatekeeper.fly.dev` |

---

## 🔒 Security Notes

- **Bcrypt hashing** (12 rounds) — passwords never stored in plaintext
- **Session protection** — `"strong"` mode invalidates sessions on IP/UA change
- **SQLAlchemy ORM** — parameterised queries prevent SQL injection
- **CSRF tokens** — on every form via WTForms
- **Audit logging** — all auth events and denied access attempts recorded with IP

---

## 📚 Learning Outcomes

Backend development, database design, authentication/authorisation, security best practices, RBAC, audit & compliance, UI/UX, error handling.

---

## 🚧 Suggested Improvements

1. **JWT-based authentication** for stateless API access
2. **OAuth2 / OpenID Connect** integration (Google, GitHub)
3. **React / Vue frontend** with role-based component visibility
4. **CSV/JSON audit log export**
5. **Many-to-many permissions table**

---

## 📄 License

MIT

---

<p align="center">
  Built with ❤️ and 🔐 security in mind.
</p>