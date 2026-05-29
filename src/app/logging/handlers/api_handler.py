from enum import Enum
import logging
import traceback
from typing import Optional

from http import HTTPStatus
import requests


from pydantic import BaseModel
from datetime import datetime

from app.core.exceptions import APIException

class LogCreate(BaseModel):
    trace_id: str
    execution_time: datetime
    message: str
    process_name: str
    status: str
    metadata_json: Optional[dict]
    #why_error: Optional[str]

class APIHandler(logging.Handler):
    def __init__(
        self,
        base_api_url: str
    ):
        super().__init__()
        self._base_api_url = base_api_url

        self._formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def _clean_metadata_json(self, record: logging.LogRecord):
        metadata_json = {
            "workflow_trace_id": getattr(record, "workflow_trace_id", None),
            "traceback_error": self._format_traceback_error(record),
            "cnpj": getattr(record, "cnpj", None),
            "input": getattr(record, "input", None),
            "output": getattr(record, "output", None),
            "count": getattr(record, "count", None),
            "result": getattr(record, "result", None),
            "fornecedores_to_update_count": getattr(record, "fornecedores_to_update_count", None),
            "successfully_built_fornecedores_count": getattr(record, "successfully_built_fornecedores_count", None),
            "failed_built_fornecedores_count": getattr(record, "failed_built_fornecedores_count", None),
            "successfully_updated_fornecedores_count": getattr(record, "successfully_updated_fornecedores_count", None),
            "failed_updated_fornecedores_count": getattr(record, "failed_updated_fornecedores_count", None),
        }
        return {k: v for k, v in metadata_json.items() if v is not None}
    def _format_traceback_error(self, record: logging.LogRecord):
        if record.exc_info:
            return "".join(traceback.format_exception(*record.exc_info))
        return None
   
    def _convert_to_api_format(self, record: logging.LogRecord):
        return LogCreate(
            trace_id=getattr(record, "trace_id", ""),
            execution_time=datetime.fromtimestamp(record.created),
            message=record.getMessage(),
            process_name=getattr(record, "event_name", record.name),
            status=record.levelname,
            metadata_json=self._clean_metadata_json(record),
        )


    def emit(self, record: logging.LogRecord):
        log_create = self._convert_to_api_format(record)

        url = f"{self._base_api_url}/api/v1/logs/"
        response = requests.post(url, json=log_create.model_dump(mode="json"))

        if response.status_code != HTTPStatus.CREATED:
            raise APIException(
                f"API returned unexpected HTTP {response.status_code}. "
                f"Response: {response.text}"
            )

        return response.json()
