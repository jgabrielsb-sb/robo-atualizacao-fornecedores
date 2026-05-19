import logging
from logging.handlers import SMTPHandler


_LOG_RECORD_BUILTIN_ATTRS = {
    "args", "created", "exc_info", "exc_text", "filename", "funcName",
    "levelname", "levelno", "lineno", "message", "module", "msecs", "msg",
    "name", "pathname", "process", "processName", "relativeCreated",
    "stack_info", "taskName", "thread", "threadName",
}

_formatter = logging.Formatter()


class DynamicSMTPHandler(SMTPHandler):
    def __init__(self, mailhost, fromaddr, toaddrs, credentials=None, secure=None, timeout=5.0):
        super().__init__(mailhost, fromaddr, toaddrs, subject="", credentials=credentials, secure=secure, timeout=timeout)

    def getSubject(self, record: logging.LogRecord) -> str:
        event_name = getattr(record, "event_name", record.name)
        return f"[Robô Atualização de Fornecedores] {record.levelname} - {event_name}"

    def _build_body(self, record: logging.LogRecord) -> str:
        lines = [
            f"Level:   {record.levelname}",
            f"Time:    {_formatter.formatTime(record)}",
            f"Logger:  {record.name}",
            f"Message: {record.getMessage()}",
        ]

        extras = {
            k: v for k, v in record.__dict__.items()
            if k not in _LOG_RECORD_BUILTIN_ATTRS
        }
        if extras:
            lines.append("\n--- Details ---")
            for k, v in extras.items():
                lines.append(f"{k}: {v}")

        if record.exc_info:
            lines.append("\n--- Traceback ---")
            lines.append(_formatter.formatException(record.exc_info))

        return "\n".join(lines)

    def format(self, record: logging.LogRecord) -> str:
        return self._build_body(record)
