# Agent Configuration

## Build/Test Commands
- **Run tests**: `pytest` or `python -m unittest discover test/`
- **Single test**: `pytest test/test_vvz.py` or `python test/test_vvz.py`
- **Backend server**: `uvicorn backend.app.app:app --reload` (from root directory)
- **Install deps**: `pip install -r requirements.txt`

## Architecture
- **Backend**: FastAPI with Beanie ODM for MongoDB
- **Database**: MongoDB with collections: users, todos, search_results
- **Models**: User (BeanieBaseUser), Todo (with UUID, owner links), SearchResult (VVZ data)
- **API**: RESTful at `/api/v1/` with authentication
- **Config**: Environment-based settings in `backend/.env`

## Code Style
- **Imports**: Group stdlib, third-party, local modules separately
- **Types**: Use Pydantic models and type hints throughout
- **Models**: Beanie Document classes with UUID fields and Links for relationships
- **Async**: Use async/await for database operations
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Environment**: Use pydantic_settings for configuration management
