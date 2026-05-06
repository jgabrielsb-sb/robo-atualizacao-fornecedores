import logging.config
from config.logging_settings import logging_settings

logging.config.dictConfig(logging_settings)

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.error("errojkjkjkr", extra={"event_name": "TESTE_EVENT", "status": "ERROR"})