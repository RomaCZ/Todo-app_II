import logging

from backend.app.core.config import settings

log_level = getattr(logging, settings.LOG_LEVEL.upper())

logging.basicConfig(format="%(levelname)s:%(message)s", level=log_level)


logger = logging.getLogger(__name__)
