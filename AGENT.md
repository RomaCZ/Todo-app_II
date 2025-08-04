# Agent Configuration

## Build/Test Commands
- **Run server**: `python run.py` or `uvicorn app.main:app --reload`
- **Install deps**: `pip install -r requirements-new.txt`
- **Run tests**: `pytest` or `python -m unittest discover test/`
- **Single test**: `pytest test/test_vvz.py` or `python test/test_vvz.py`
- **Database migration**: `alembic upgrade head`

## Architecture
- **Backend**: FastAPI with SQLModel and PostgreSQL
- **Database**: PostgreSQL with contracts table
- **Models**: Contract (SQLModel) with external_id, publication dates, processing status
- **API**: RESTful at `/api/v1/` (contracts, crawler endpoints)
- **Frontend**: Static HTML dashboard at `/static/index.html`
- **Crawler**: Background scheduler + manual triggers, uses zakazka/vvz.py
- **Config**: Environment-based settings in `.env`

## Code Style
- **Imports**: Group stdlib, third-party, local modules separately
- **Types**: Use SQLModel and type hints throughout
- **Models**: SQLModel classes with optional primary keys and timestamps
- **Async**: Use async/await for database and HTTP operations
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Environment**: Use pydantic_settings for configuration management
