
from logging.handlers import SMTPHandler
from app.logging.handlers.smtp_handler import DynamicSubjectSMTPHandler
from config.settings import settings


logging_settings = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {},
    "formatters": {
        "simple": {
            "format": "[%(levelname)s] [%(asctime)s]: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        },
        "json": {
            "()": "app.logging.formatters.JSONFormatter",
            "fmt_keys": {
                "level": "levelname",
                "timestamp": "timestamp",
                "message": "message",
                "exc_info": "exc_info",
                "stack_info": "stack_info"
            }
        },
    },
    "handlers": {
        "stder": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stderr"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "json",
            "filename": "logs/my_app.log.jsonl",
            "maxBytes": 10000,
            "backupCount": 3,
        },
        "smtp": {
            "class": "app.logging.handlers.smtp_handler.DynamicSubjectSMTPHandler",
            "level": "ERROR",
            "formatter": "json",
            "subject": "XXX",
            "mailhost": (settings.EMAIL_HOST, settings.EMAIL_PORT),
            "fromaddr": settings.EMAIL_HOST_USER,
            "toaddrs": ['jgabrielsb2002@gmail.com'],
            "credentials": (settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD),
            "secure": () if settings.EMAIL_IS_TLS else None
        }
    },
    "loggers": {
        "root": {"level": "INFO", "handlers": ["stder", "file"]}
    }
}
