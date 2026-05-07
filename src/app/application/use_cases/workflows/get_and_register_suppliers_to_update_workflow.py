"""
The is the workflow that is responsible for getting the 'Fornecedores' on Protheus that must be updated.
Then, the 'Fornecedores' are registered on the database and marked as 'to update'.
"""

import logging
import uuid
from pydantic import BaseModel

from app.domain.enums import StatusEnum
from app.application.ports import (
    GetFornecedoresToUpdatePort, 
    FornecedorToUpdateRepositoryPort,
    FornecedorToUpdate,
)

logger = logging.getLogger(__name__)

class GetAndRegisterFornecedoresToUpdateWorkflowError(Exception):
    pass

class GetFornecedoresToUpdateWorkflowError(GetAndRegisterFornecedoresToUpdateWorkflowError):
    pass

class SaveFornecedorToUpdateWorkflowError(GetAndRegisterFornecedoresToUpdateWorkflowError):
    pass


class GetAndRegisterFornecedoresToUpdateWorkflowResult(BaseModel):
    workflow_trace_id: str
    fornecedores_to_update_count: int
    registered_fornecedores_count: int
    failed_fornecedores_count: int


GET_FORNECEDORES_TO_UPDATE_EVENT_NAME = "GET_FORNECEDORES_TO_UPDATE"
SAVE_FORNECEDOR_TO_UPDATE_EVENT_NAME = "SAVE_FORNECEDOR_TO_UPDATE"
WORKFLOW_EVENT_NAME = "GET_AND_REGISTER_FORNECEDORES_TO_UPDATE"

class GetAndRegisterFornecedoresToUpdateWorkflow:
    def __init__(
        self,
        get_fornecedores_to_update: GetFornecedoresToUpdatePort,
        fornecedor_to_update_repository: FornecedorToUpdateRepositoryPort,
    ):
        self._get_fornecedores_to_update = get_fornecedores_to_update
        self._fornecedor_to_update_repository = fornecedor_to_update_repository

    def get_fornecedores_to_update(
        self, 
        workflow_trace_id: str
    ) -> list[FornecedorToUpdate]:
        EVENT_NAME = GET_FORNECEDORES_TO_UPDATE_EVENT_NAME
        try:
            fornecedores_to_update = self._get_fornecedores_to_update.get()
            logger.info(
                "Successfully retrieved fornecedores to update", 
                extra={
                    "workflow_trace_id": workflow_trace_id,
                    "count": len(fornecedores_to_update),
                    "result": [str(fornecedor) for fornecedor in fornecedores_to_update],
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                }
            )
            return fornecedores_to_update
        except Exception as e:
            logger.error(
                "Failed to retrieve fornecedores to update",
                extra={
                    "workflow_trace_id": workflow_trace_id,
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                },
                exc_info=True,
            )
            raise GetFornecedoresToUpdateWorkflowError(
                f"Failed to retrieve fornecedores to update: {e}"
            ) from e

    def save_fornecedor_to_update(
        self, 
        fornecedor: FornecedorToUpdate, 
        workflow_trace_id: str
    ) -> None:
        EVENT_NAME = SAVE_FORNECEDOR_TO_UPDATE_EVENT_NAME
        try:
            result = self._fornecedor_to_update_repository.save(fornecedor)
            logger.info(
                "Successfully saved fornecedor to update",
                extra={
                    "workflow_trace_id": workflow_trace_id,
                    "result": str(result),
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                    "fornecedor": str(fornecedor),
                }
            )
        except Exception as e:
            logger.error(
                "Failed to save fornecedor to update",
                extra={
                    "workflow_trace_id": workflow_trace_id,
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                    "fornecedor": str(fornecedor),
                },
                exc_info=True,
            )
            raise SaveFornecedorToUpdateWorkflowError(
                f"Failed to save fornecedor to update"
            ) from e

    def _log_result(
        self,
        result: GetAndRegisterFornecedoresToUpdateWorkflowResult,
    ) -> None:
        status = (
            StatusEnum.SUCCESS.value
            if result.failed_fornecedores_count == 0
            else StatusEnum.WARNING.value
        )

        message = (
            "Successfully registered all fornecedores to update"
            if result.failed_fornecedores_count == 0
            else "Failed to register some fornecedores to update"
        )

        log_method = logger.info if result.failed_fornecedores_count == 0 else logger.warning

        log_method(
            message,
            extra={
                "workflow_trace_id": result.workflow_trace_id,
                "status": status,
                "event_name": WORKFLOW_EVENT_NAME,
                "fornecedores_to_update_count": result.fornecedores_to_update_count,
                "registered_fornecedores_count": result.registered_fornecedores_count,
                "failed_fornecedores_count": result.failed_fornecedores_count,
            },
        )

    def run(self) -> GetAndRegisterFornecedoresToUpdateWorkflowResult:
        workflow_trace_id = str(uuid.uuid4())

        fornecedores_to_update = self.get_fornecedores_to_update(workflow_trace_id)

        registered_fornecedores_count = 0
        failed_fornecedores_count = 0

        for fornecedor in fornecedores_to_update:
            try:
                self.save_fornecedor_to_update(fornecedor, workflow_trace_id)
                registered_fornecedores_count += 1
            except SaveFornecedorToUpdateWorkflowError:
               failed_fornecedores_count += 1
               continue
           
        result = GetAndRegisterFornecedoresToUpdateWorkflowResult(
            workflow_trace_id=workflow_trace_id,
            fornecedores_to_update_count=len(fornecedores_to_update),
            registered_fornecedores_count=registered_fornecedores_count,
            failed_fornecedores_count=failed_fornecedores_count,
        )
        self._log_result(result)
        return result

        

