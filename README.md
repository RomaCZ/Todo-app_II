# VVZ Crawler Service

A modern FastAPI web service for crawling and managing public procurement contracts from Věstník veřejných zakázek (VVZ).

## Features

- **Automated Crawling**: Periodic background crawling of VVZ contracts
- **Web Dashboard**: Simple web interface for viewing and managing contracts
- **RESTful API**: Full API for programmatic access
- **Database Storage**: PostgreSQL database for persistent storage
- **Manual Controls**: Manual crawling triggers and contract processing

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-new.txt
```

### 2. Set up Environment

```bash
cp .env.example .env
# Edit .env with your database connection and settings
```

### 3. Set up PostgreSQL Database

```bash
# Create database named 'vvz_crawler'
createdb vvz_crawler
```

### 4. Run the Service

```bash
python run.py
```

The service will be available at:
- **Web Dashboard**: http://localhost:8000/static/index.html
- **API Documentation**: http://localhost:8000/docs

## API Endpoints

### Contracts
- `GET /api/v1/contracts/` - List contracts with filtering
- `GET /api/v1/contracts/{id}` - Get specific contract
- `PATCH /api/v1/contracts/{id}` - Update contract (mark as processed)
- `GET /api/v1/contracts/stats/summary` - Get contract statistics

### Crawler
- `POST /api/v1/crawler/manual-crawl` - Trigger manual crawl for date range
- `POST /api/v1/crawler/crawl-today` - Crawl today's contracts
- `GET /api/v1/crawler/status` - Get crawler status

## Configuration

Environment variables in `.env`:

- `DATABASE_URL` - PostgreSQL connection string
- `CRAWLER_INTERVAL_MINUTES` - How often to run automatic crawling (default: 60)
- `VVZ_API_BASE_URL` - VVZ API base URL
- `LOG_LEVEL` - Logging level

## Architecture

```
app/
├── main.py              # FastAPI application
├── core/
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database connection
│   └── scheduler.py     # Background task scheduler
├── models/
│   └── contract.py      # SQLModel database models
├── services/
│   └── crawler.py       # Crawler service logic
├── api/v1/
│   └── endpoints/       # API endpoints
└── static/
    └── index.html       # Web dashboard

zakazka/                 # Legacy crawler logic (reused)
├── vvz.py              # VVZ API crawler
├── zakazky_III.py      # Contract processing logic
└── ...                 # Supporting modules
```

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

If you need to modify the database schema, you can use Alembic:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Usage

1. **Access the Dashboard**: Open http://localhost:8000/static/index.html
2. **Select Date Range**: Choose the dates you want to view contracts for
3. **Filter Contracts**: Use the filters for contract type and processing status
4. **Manual Crawling**: Use the "Manual Crawl" button to fetch new contracts
5. **Mark as Processed**: Click the action buttons to mark contracts as processed/unprocessed

The service will automatically crawl for new contracts every hour (configurable).
