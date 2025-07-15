# Copilot Instructions for JobMateRefactor

## Project Overview
JobMateRefactor is an AI-powered job matching platform for Ontario's tech sector, built with Flask (Python), Bootstrap, and AI integrations. It supports two user types: Applicants (Job Seekers) and Recruiters (Hiring Managers), each with dedicated dashboards and workflows.

## Architecture & Key Components
- **Flask app structure**: Modularized with Blueprints for `auth`, `main`, `resume`, `jobs`, `match`, `profile`, `recruiter`, etc. See `app/` for modules and `app/__init__.py` for the factory pattern.
- **Data models**: Located in `app/models/` (PostgreSQL via SQLAlchemy for core data, MongoDB for some job data).
- **Templates**: Jinja2 templates in `templates/` (e.g., `dashboard/`, `auth/`, `main/`, `resume/`).
- **Static assets**: Custom CSS/JS in `static/`.
- **Database scripts**: `database/init.sql` (PostgreSQL), `database/mongo-init.js` (MongoDB).
- **AI Integration**: See `app/ai_agents/` for resume parsing and job matching logic.
- **Entry point**: `run.py`.

## Developer Workflows
- **Setup**: Use Python 3.11+, install dependencies from `requirements.txt`, configure `.env` (see `env.example`).
- **Database**: Initialize PostgreSQL and MongoDB using scripts in `database/`. Run Alembic migrations with `flask db upgrade`.
- **Run**: Start with `python run.py` (default port 5002).
- **Testing**: Use `pytest` for unit tests, `pytest --cov=app` for coverage, and Playwright for integration tests.
- **Docker**: Use `docker-compose up --build` for full stack, or `docker-compose up postgres mongodb redis` for services only.
- **CI/CD**: GitHub Actions in `.github/workflows/` for linting, tests, and deployment.

## Project-Specific Patterns & Conventions
- **Blueprints**: All major features are separated into Flask Blueprints for modularity.
- **Forms**: WTForms for validation (`app/auth/forms.py`).
- **User roles**: Role-based dashboards and navigation (see `app/main/routes.py`, `templates/dashboard/`).
- **AI/Resume logic**: Encapsulated in `app/ai_agents/`.
- **Job data**: Some job data is stored in MongoDB for flexibility.
- **Testing**: Test files are at the root (e.g., `test_login_with_logs.py`).
- **Environment variables**: Managed via `.env` (see `env.example`).

## Integration Points & External Dependencies
- **PostgreSQL**: Main relational database.
- **MongoDB**: Used for job postings and possibly analytics.
- **Google AI API**: For resume parsing and job matching (see `GOOGLE_API_KEY`).
- **Email**: SMTP for password reset and notifications.
- **Redis/Celery**: Optional for background tasks.

## Examples
- To add a new feature, create a new Blueprint in `app/`, register it in `app/__init__.py`, and add templates/static assets as needed.
- To add a new model, define it in `app/models/`, create a migration, and update the database.
- To add a new test, create a file at the project root or in a `tests/` folder.

## References
- See `README.md` for setup, architecture, and workflow details.
- See `docs/` for feature set, architecture, and workflows.
- See `app/ai_agents/` for AI integration logic.

---

If you are unsure about a pattern or integration, check the relevant module in `app/` or the documentation in `docs/`.
