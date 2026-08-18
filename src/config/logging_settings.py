
from logging.handlers import SMTPHandler
from app.logging.handlers.smtp_handler import DynamicSMTPHandler
from config.settings import settings


logging_settings = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {},
    "root": {"level": "INFO", "handlers": ["stder", "file"]},
    "loggers": {
        "app.application.use_cases.workflows.get_and_update_fornecedores_workflow": {
            "level": "INFO",
            "handlers": ["api", "smtp"],
            "propagate": True,
        },
        "main": {
            "level": "INFO",
            "handlers": ["smtp"],
            "propagate": True,
        }
    },
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
            "class": "app.logging.handlers.smtp_handler.DynamicSMTPHandler",
            "level": "ERROR",
            "formatter": "json",
            "mailhost": (settings.EMAIL_HOST, settings.EMAIL_PORT),
            "fromaddr": settings.EMAIL_HOST_USER,
            "toaddrs": ['jgabrielsb2002@gmail.com'],
            "credentials": (settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD),
            "secure": () if settings.EMAIL_IS_TLS else None
        },
        "api": {
            "class": "app.logging.handlers.api_handler.APIHandler",
            "level": "INFO",
            "base_api_url": settings.FORNECEDORES_API_BASE_URL
        }
    },
}
