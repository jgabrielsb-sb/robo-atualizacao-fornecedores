"""
Workflow responsible for retrieving the 'Fornecedores' that must be updated,
building their full data via an external port, and persisting the updated records.
"""

import logging
import uuid
from pydantic import BaseModel

from app.domain.enums import StatusEnum
from app.domain.entities import Fornecedor

from app.application.ports import (
    GetFornecedoresToUpdatePort, 
    FornecedorRepositoryPort,
    FornecedorToUpdate,
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
    workflow_trace_id: str
    fornecedores_to_update_count: int
    successfully_built_fornecedores_count: int
    failed_built_fornecedores_count: int
    successfully_updated_fornecedores_count: int
    failed_updated_fornecedores_count: int


GET_FORNECEDORES_TO_UPDATE_EVENT_NAME = "GET_FORNECEDORES_TO_UPDATE"
BUILD_FORNECEDOR_EVENT_NAME = "BUILD_FORNECEDOR"
UPDATE_FORNECEDOR_EVENT_NAME = "UPDATE_FORNECEDOR"
WORKFLOW_EVENT_NAME = "GET_AND_UPDATE_FORNECEDORES"

class GetAndUpdateFornecedoresWorkflow:
    def __init__(
        self,
        get_fornecedores_to_update: GetFornecedoresToUpdatePort,
        build_fornecedor: BuildFornecedorPort,
        fornecedor_repository: FornecedorRepositoryPort,
    ):
        self._get_fornecedores_to_update = get_fornecedores_to_update
        self._build_fornecedor = build_fornecedor
        self._fornecedor_repository = fornecedor_repository

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

    def build_fornecedor(
        self,
        fornecedor_to_update: FornecedorToUpdate,
        workflow_trace_id: str
    ) -> Fornecedor:
        EVENT_NAME = BUILD_FORNECEDOR_EVENT_NAME
        try:
            fornecedor = self._build_fornecedor.build(fornecedor_to_update.cnpj)
            logger.info(
                "Successfully built fornecedor",
                extra={
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_to_update": str(fornecedor_to_update),
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                },
            )
            return fornecedor
        except Exception as e:
            logger.error(
                "Failed to build fornecedor",
                extra={
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_to_update": str(fornecedor_to_update),
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
        workflow_trace_id: str
    ) -> None:
        EVENT_NAME = UPDATE_FORNECEDOR_EVENT_NAME
        try:
            result = self._fornecedor_repository.update(fornecedor)
            logger.info(
                "Successfully updated fornecedor",
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
                "Failed to update fornecedor",
                extra={
                    "workflow_trace_id": workflow_trace_id,
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                    "fornecedor": str(fornecedor),
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
                "workflow_trace_id": result.workflow_trace_id,
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

        for fornecedor in fornecedores_to_update:
            try:
                fornecedor = self.build_fornecedor(fornecedor, workflow_trace_id)
                successfully_built_fornecedores_count += 1
            except BuildFornecedorWorkflowError:
                failed_built_fornecedores_count += 1
                continue

            try:
                self.update_fornecedor(fornecedor, workflow_trace_id)
                successfully_updated_fornecedores_count += 1
            except UpdateFornecedorWorkflowError:
               failed_updated_fornecedores_count += 1
               continue
           
        result = GetAndUpdateFornecedoresWorkflowResult(
            workflow_trace_id=workflow_trace_id,
            fornecedores_to_update_count=len(fornecedores_to_update),
            successfully_built_fornecedores_count=successfully_built_fornecedores_count,
            failed_built_fornecedores_count=failed_built_fornecedores_count,
            successfully_updated_fornecedores_count=successfully_updated_fornecedores_count,
            failed_updated_fornecedores_count=failed_updated_fornecedores_count,
        )
        self._log_result(result)
        return result

        

