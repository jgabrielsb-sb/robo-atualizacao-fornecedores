"""
Workflow responsible for retrieving the CNPJs that must be updated,
building their full Fornecedor data via an external port, and persisting the updated records.
"""
import json
import logging
import uuid
from dataclasses import asdict
from pydantic import BaseModel

from app.domain.enums import StatusEnum
from app.domain.entities import Fornecedor
from app.domain.value_objects import CNPJ

from app.application.ports import (
    GetFornecedoresToUpdatePort,
    UpdateFornecedorPort,
    BuildFornecedorPort,
)

logger = logging.getLogger(__name__)

class GetAndUpdateFornecedoresWorkflowError(Exception):
    pass

class GetFornecedoresToUpdateWorkflowError(GetAndUpdateFornecedoresWorkflowError):
    pass

class BuildFornecedorWorkflowError(GetAndUpdateFornecedoresWorkflowError):
    pass

class UpdateFornecedorWorkflowError(GetAndUpdateFornecedoresWorkflowError):
    pass


class GetAndUpdateFornecedoresWorkflowResult(BaseModel):
    trace_id: str
    fornecedores_to_update_count: int
    successfully_built_fornecedores_count: int
    failed_built_fornecedores_count: int
    successfully_updated_fornecedores_count: int
    failed_updated_fornecedores_count: int


def _fornecedor_as_json(fornecedor: Fornecedor) -> dict:
    """asdict() alone leaves Enum/UUID objects embedded, which aren't JSON-serializable;
    round-tripping through json.dumps/loads guarantees a genuinely JSON-safe dict for logging."""
    return json.loads(json.dumps(asdict(fornecedor), default=str))


GET_FORNECEDORES_TO_UPDATE_EVENT_NAME = "GET_FORNECEDORES_TO_UPDATE"
BUILD_FORNECEDOR_EVENT_NAME = "BUILD_FORNECEDOR"
UPDATE_FORNECEDOR_EVENT_NAME = "UPDATE_FORNECEDOR"
WORKFLOW_EVENT_NAME = "GET_AND_UPDATE_FORNECEDORES"

class GetAndUpdateFornecedoresWorkflow:
    def __init__(
        self,
        get_fornecedores_to_update: GetFornecedoresToUpdatePort,
        build_fornecedor: BuildFornecedorPort,
        update_fornecedor: UpdateFornecedorPort,
    ):
        self._get_fornecedores_to_update = get_fornecedores_to_update
        self._build_fornecedor = build_fornecedor
        self._update_fornecedor = update_fornecedor

    def get_fornecedores_to_update(
        self,
        workflow_trace_id: str,
    ) -> list[Fornecedor]:
        trace_id = str(uuid.uuid4())
        EVENT_NAME = GET_FORNECEDORES_TO_UPDATE_EVENT_NAME
        try:
            fornecedores_to_update = self._get_fornecedores_to_update.get()
            logger.info(
                "Successfully retrieved fornecedores to update",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "count": len(fornecedores_to_update),
                    "output": [fornecedor.identificacao.cnpj.value for fornecedor in fornecedores_to_update],
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                }
            )
            return fornecedores_to_update
        except Exception as e:
            logger.error(
                "Failed to retrieve fornecedores to update",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                },
                exc_info=True,
            )
            raise GetFornecedoresToUpdateWorkflowError(
                f"Failed to retrieve fornecedores to update: {e}"
            ) from e

    def build_fornecedor(
        self,
        fornecedor: Fornecedor,
        workflow_trace_id: str,
        fornecedor_trace_id: str,
    ) -> Fornecedor:
        trace_id = str(uuid.uuid4())
        EVENT_NAME = BUILD_FORNECEDOR_EVENT_NAME
        cnpj = fornecedor.identificacao.cnpj
        try:
            fornecedor = self._build_fornecedor.build(cnpj)
            logger.info(
                "Successfully built fornecedor",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": cnpj.value,
                    "input": _fornecedor_as_json(fornecedor),
                    "output": _fornecedor_as_json(fornecedor),
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                },
            )
            return fornecedor
        except Exception as e:
            logger.error(
                "Failed to build fornecedor",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id, 
                    "fornecedor_cnpj": cnpj.value,
                    "input": _fornecedor_as_json(fornecedor),
                    "output": None,
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                },
                exc_info=True,
            )
            raise BuildFornecedorWorkflowError(
                f"Failed to build fornecedor: {e}"
            ) from e

    def update_fornecedor(
        self,
        fornecedor: Fornecedor,
        workflow_trace_id: str,
        fornecedor_trace_id: str,
    ) -> None:
        trace_id = str(uuid.uuid4())
        EVENT_NAME = UPDATE_FORNECEDOR_EVENT_NAME
        try:
            result = self._update_fornecedor.update(fornecedor)
            logger.info(
                "Successfully updated fornecedor",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": fornecedor.identificacao.cnpj.value,
                    "input": _fornecedor_as_json(fornecedor),
                    "output": "TESTE MUDAR",
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                }
            )
        except Exception as e:
            logger.error(
                "Failed to update fornecedor",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": fornecedor.identificacao.cnpj.value,
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                    "input": _fornecedor_as_json(fornecedor),
                    "output": None,
                },
                exc_info=True,
            )
            raise UpdateFornecedorWorkflowError(
                f"Failed to update fornecedor"
            ) from e

    def _log_result(
        self,
        result: GetAndUpdateFornecedoresWorkflowResult,
    ) -> None:
        all_succeeded = (
            result.failed_built_fornecedores_count == 0
            and result.failed_updated_fornecedores_count == 0
        )

        status = StatusEnum.SUCCESS.value if all_succeeded else StatusEnum.WARNING.value
        message = "Successfully updated all fornecedores" if all_succeeded else "Failed to update some fornecedores"
        log_method = logger.info if all_succeeded else logger.warning

        log_method(
            message,
            extra={
                "trace_id": result.trace_id,
                "status": status,
                "event_name": WORKFLOW_EVENT_NAME,
                "fornecedores_to_update_count": result.fornecedores_to_update_count,
                "successfully_built_fornecedores_count": result.successfully_built_fornecedores_count,
                "failed_built_fornecedores_count": result.failed_built_fornecedores_count,
                "successfully_updated_fornecedores_count": result.successfully_updated_fornecedores_count,
                "failed_updated_fornecedores_count": result.failed_updated_fornecedores_count,
            },
        )

    def run(self) -> GetAndUpdateFornecedoresWorkflowResult:
        workflow_trace_id = str(uuid.uuid4())

        fornecedores_to_update = self.get_fornecedores_to_update(workflow_trace_id)

        successfully_built_fornecedores_count = 0
        failed_built_fornecedores_count = 0

        successfully_updated_fornecedores_count = 0
        failed_updated_fornecedores_count = 0

        for fornecedor_to_update in fornecedores_to_update:
            fornecedor_trace_id = str(uuid.uuid4())
            try:
                fornecedor = self.build_fornecedor(
                    fornecedor_to_update, 
                    workflow_trace_id,
                    fornecedor_trace_id
                )
                successfully_built_fornecedores_count += 1
            except BuildFornecedorWorkflowError:
                failed_built_fornecedores_count += 1
                continue

            try:
                self.update_fornecedor(
                    fornecedor, 
                    workflow_trace_id,
                    fornecedor_trace_id
                )
                successfully_updated_fornecedores_count += 1
            except UpdateFornecedorWorkflowError:
                failed_updated_fornecedores_count += 1
                continue

        result = GetAndUpdateFornecedoresWorkflowResult(
            trace_id=workflow_trace_id,
            fornecedores_to_update_count=len(fornecedores_to_update),
            successfully_built_fornecedores_count=successfully_built_fornecedores_count,
            failed_built_fornecedores_count=failed_built_fornecedores_count,
            successfully_updated_fornecedores_count=successfully_updated_fornecedores_count,
            failed_updated_fornecedores_count=failed_updated_fornecedores_count,
        )
        self._log_result(result)
        return result
