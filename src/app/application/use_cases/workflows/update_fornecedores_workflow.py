"""
This is the workflow responsible for updating the 'Fornecedores' in the system.
It retrieves the fornecedores marked as 'to update', fetches their full data via an external port,
and persists the updated records through the repository port.
"""

import logging
import uuid
from pydantic import BaseModel

from app.domain.enums import StatusEnum
from app.domain.entities import Fornecedor
from app.application.ports import (
    GetFornecedoresToUpdatePort,
    FornecedorToUpdate,
    BuildFornecedorPort,
    BuildFornecedorInput,
    FornecedorRepositoryPort,
)

logger = logging.getLogger(__name__)


class UpdateFornecedoresWorkflowError(Exception):
    pass


class GetFornecedoresToUpdateWorkflowError(UpdateFornecedoresWorkflowError):
    pass


class BuildFornecedorWorkflowError(UpdateFornecedoresWorkflowError):
    pass


class UpdateFornecedorWorkflowError(UpdateFornecedoresWorkflowError):
    pass


class UpdateFornecedoresWorkflowResult(BaseModel):
    workflow_trace_id: str
    status: StatusEnum
    fornecedores_to_update_count: int = 0
    successfully_built_fornecedores_count: int = 0
    failed_built_fornecedores_count: int = 0
    successfully_updated_fornecedores_count: int = 0
    failed_updated_fornecedores_count: int = 0


GET_FORNECEDORES_TO_UPDATE_EVENT_NAME = "GET_FORNECEDORES_TO_UPDATE"
BUILD_FORNECEDOR_EVENT_NAME = "BUILD_FORNECEDOR"
UPDATE_FORNECEDOR_EVENT_NAME = "UPDATE_FORNECEDOR"
WORKFLOW_EVENT_NAME = "UPDATE_FORNECEDORES"


class UpdateFornecedoresWorkflow:
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
        workflow_trace_id: str,
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
                },
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

    def _build_fornecedor_input(
        self,
        fornecedor_to_update: FornecedorToUpdate,
    ) -> BuildFornecedorInput:
        """
        Maps a FornecedorToUpdate into a BuildFornecedorInput.

        This method exists because the exact input shape may change later.
        When the BuildFornecedorInput becomes more complete, change only this
        method instead of changing the workflow orchestration.
        """
        return BuildFornecedorInput(
            id=fornecedor_to_update.id,
        )
        

    def build_fornecedor(
        self,
        fornecedor_to_update: FornecedorToUpdate,
        workflow_trace_id: str,
    ) -> Fornecedor:
        EVENT_NAME = BUILD_FORNECEDOR_EVENT_NAME
        try:
            fornecedor_input = self._build_fornecedor_input(fornecedor_to_update)
            fornecedor = self._build_fornecedor.build(fornecedor_input)
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
        workflow_trace_id: str,
    ) -> None:
        EVENT_NAME = UPDATE_FORNECEDOR_EVENT_NAME
        try:
            self._fornecedor_repository.update(fornecedor)
            logger.info(
                "Successfully updated fornecedor",
                extra={
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor": str(fornecedor),
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                },
            )
        except Exception as e:
            logger.error(
                "Failed to update fornecedor",
                extra={
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor": str(fornecedor),
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                },
                exc_info=True,
            )
            raise UpdateFornecedorWorkflowError(
                f"Failed to update fornecedor"
            ) from e

    def _log_result(
        self,
        result: UpdateFornecedoresWorkflowResult,
    ) -> None:
        status = (
            StatusEnum.SUCCESS.value
            if result.failed_built_fornecedores_count == 0 
            and result.failed_updated_fornecedores_count == 0
            else StatusEnum.WARNING.value
        )

        message = (
            "Successfully updated all fornecedores"
            if result.failed_built_fornecedores_count == 0 
            and result.failed_updated_fornecedores_count == 0
            else "Failed to update some fornecedores"
        )

        log_method = (
            logger.info 
            if result.failed_built_fornecedores_count == 0 
            and result.failed_updated_fornecedores_count == 0 
            else logger.warning
        )

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

    def run(self) -> UpdateFornecedoresWorkflowResult:
        workflow_trace_id = str(uuid.uuid4())
        
        successfully_updated_fornecedores_count, failed_updated_fornecedores_count = 0, 0
        successfully_built_fornecedores_count, failed_built_fornecedores_count = 0, 0

        try:
            fornecedores_to_update = self.get_fornecedores_to_update(workflow_trace_id)
        except GetFornecedoresToUpdateWorkflowError:
            return UpdateFornecedoresWorkflowResult(
                workflow_trace_id=workflow_trace_id,
                status=StatusEnum.ERROR,
                
            )

        for fornecedor_to_update in fornecedores_to_update:
            try:
                fornecedor = self.build_fornecedor(fornecedor_to_update, workflow_trace_id)
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

        result = UpdateFornecedoresWorkflowResult(
            workflow_trace_id=workflow_trace_id,
            status=StatusEnum.SUCCESS if failed_built_fornecedores_count == 0 and failed_updated_fornecedores_count == 0 else StatusEnum.PARTIAL,
            fornecedores_to_update_count=len(fornecedores_to_update),
            successfully_updated_fornecedores_count=successfully_updated_fornecedores_count,
            failed_updated_fornecedores_count=failed_updated_fornecedores_count,
            successfully_built_fornecedores_count=successfully_built_fornecedores_count,
            failed_built_fornecedores_count=failed_built_fornecedores_count,
        )
        
        self._log_result(result)
        return result
