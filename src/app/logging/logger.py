import logging.config
from config.logging_settings import logging_settings

logging.config.dictConfig(logging_settings)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        result = 1 / 0
    except Exception as e:
        logger.error("error", exc_info=e)
    