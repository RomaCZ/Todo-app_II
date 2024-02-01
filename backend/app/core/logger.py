import logging
from json import dumps as json_dumps
from pathlib import Path

from backend.app.core.config import settings

app_name = settings.PROJECT_NAME

log_format_json = {
    "timestamp": "%(asctime)s",
    "level": "%(levelname)s",
    "message": "%(message)s",
    "funcName": "%(funcName)s",
    "lineno": "%(lineno)d",
}

log_format_console = "%(asctime)s - %(levelname)s - %(message)s"

log_level = getattr(logging, settings.LOG_LEVEL.upper())
log_dir = Path.home() / "logs"
log_filename = f"{app_name}.log"
log_file = log_dir / log_filename
log_dir.mkdir(exist_ok=True)

file_formatter = json_dumps(log_format_json)
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter(file_formatter))

stream_formatter = log_format_console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(stream_formatter))

logger = logging.getLogger(app_name)
logger.setLevel(log_level)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
