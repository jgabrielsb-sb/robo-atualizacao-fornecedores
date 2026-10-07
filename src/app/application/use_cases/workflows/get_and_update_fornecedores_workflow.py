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
    UpdatedFornecedorRepositoryPort,
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

class PersistUpdatedFornecedorWorkflowError(GetAndUpdateFornecedoresWorkflowError):
    pass


class GetAndUpdateFornecedoresWorkflowResult(BaseModel):
    trace_id: str
    fornecedores_to_update_count: int
    successfully_built_fornecedores_count: int
    failed_built_fornecedores_count: int
    successfully_updated_fornecedores_count: int
    failed_updated_fornecedores_count: int
    successfully_persisted_fornecedores_count: int
    failed_persisted_fornecedores_count: int


def _fornecedor_as_json(fornecedor: Fornecedor) -> dict:
    """asdict() alone leaves Enum/UUID objects embedded, which aren't JSON-serializable;
    round-tripping through json.dumps/loads guarantees a genuinely JSON-safe dict for logging."""
    return json.loads(json.dumps(asdict(fornecedor), default=str))


GET_FORNECEDORES_TO_UPDATE_EVENT_NAME = "GET_FORNECEDORES_TO_UPDATE"
BUILD_FORNECEDOR_EVENT_NAME = "BUILD_FORNECEDOR"
UPDATE_FORNECEDOR_EVENT_NAME = "UPDATE_FORNECEDOR"
PERSIST_UPDATED_FORNECEDOR_EVENT_NAME = "PERSIST_UPDATED_FORNECEDOR"
WORKFLOW_EVENT_NAME = "GET_AND_UPDATE_FORNECEDORES"

class GetAndUpdateFornecedoresWorkflow:
    def __init__(
        self,
        get_fornecedores_to_update: GetFornecedoresToUpdatePort,
        build_fornecedor: BuildFornecedorPort,
        update_fornecedor: UpdateFornecedorPort,
        persist_updated_fornecedor: UpdatedFornecedorRepositoryPort,
    ):
        self._get_fornecedores_to_update = get_fornecedores_to_update
        self._build_fornecedor = build_fornecedor
        self._update_fornecedor = update_fornecedor
        self._persist_updated_fornecedor = persist_updated_fornecedor

    def get_fornecedores_to_update(
        self,
        workflow_trace_id: str,
    ) -> list[Fornecedor]:
        logger.info('Getting all the fornecedores that must be updated...')
        
        trace_id = str(uuid.uuid4())
        EVENT_NAME = GET_FORNECEDORES_TO_UPDATE_EVENT_NAME
        try:
            fornecedores_to_update = self._get_fornecedores_to_update.get()
            logger.info(
                f"Successfully retrieved fornecedores to update. There are {len(fornecedores_to_update)} fornecedores to update.",
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
                f"(TRACE_ID: {trace_id}) Failed to retrieve fornecedores to update",
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
            fornecedor_after_build = self._build_fornecedor.build(cnpj)
            logger.info(
                f"(TRACE_ID: {trace_id}) Successfully built fornecedor with CNPJ {fornecedor.identificacao.cnpj.value} with updated informations",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": cnpj.value,
                    "input": _fornecedor_as_json(fornecedor),
                    "output": _fornecedor_as_json(fornecedor_after_build),
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                },
            )
            return fornecedor_after_build
        except Exception as e:
            logger.error(
                f"(TRACE_ID: {trace_id}) Failed to build fornecedor with CNPJ {fornecedor.identificacao.cnpj.value} with updated informations",
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
                f"(TRACE_ID: {trace_id}) Successfully updated fornecedor with CNPJ {fornecedor.identificacao.cnpj.value} on Protheus",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": fornecedor.identificacao.cnpj.value,
                    "input": _fornecedor_as_json(fornecedor),
                    "output": result,
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                }
            )
        except Exception as e:
            logger.error(
                f"(TRACE_ID: {trace_id}) Failed to update fornecedor with CNPJ {fornecedor.identificacao.cnpj.value} on Protheus",
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

    def persist_updated_fornecedor(
        self,
        fornecedor: Fornecedor,
        workflow_trace_id: str,
        fornecedor_trace_id: str,
    ) -> None:
        trace_id = str(uuid.uuid4())
        EVENT_NAME = PERSIST_UPDATED_FORNECEDOR_EVENT_NAME
        cnpj = fornecedor.identificacao.cnpj
        try:
            result = self._persist_updated_fornecedor.create(cnpj)
            logger.info(
                f"(TRACE_ID: {trace_id}) Successfully persisted updated fornecedor with CNPJ {fornecedor.identificacao.cnpj.value} on Fornecedores API",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": cnpj.value,
                    "input": cnpj.value,
                    "output": result.model_dump(mode="json"),
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                }
            )
        except Exception as e:
            logger.error(
                f"(TRACE_ID: {trace_id}) Failed to persist updated fornecedor with CNPJ {fornecedor.identificacao.cnpj.value} on Fornecedores API",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": cnpj.value,
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                    "input": cnpj.value,
                    "output": None,
                },
                exc_info=True,
            )
            raise PersistUpdatedFornecedorWorkflowError(
                f"Failed to persist updated fornecedor with CNPJ {fornecedor.identificacao.cnpj.value} on Fornecedores API"
            ) from e

    def _log_result(
        self,
        result: GetAndUpdateFornecedoresWorkflowResult,
    ) -> None:
        all_succeeded = (
            result.failed_built_fornecedores_count == 0
            and result.failed_updated_fornecedores_count == 0
            and result.failed_persisted_fornecedores_count == 0
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
                "successfully_persisted_fornecedores_count": result.successfully_persisted_fornecedores_count,
                "failed_persisted_fornecedores_count": result.failed_persisted_fornecedores_count,
            },
        )

    def run(self) -> GetAndUpdateFornecedoresWorkflowResult:
        logger.info("Running the GetAndUpdateFornecedoresWorkflow")

        workflow_trace_id = str(uuid.uuid4())

        fornecedores_to_update = self.get_fornecedores_to_update(workflow_trace_id)[:100]

        successfully_built_fornecedores_count = 0
        failed_built_fornecedores_count = 0

        successfully_updated_fornecedores_count = 0
        failed_updated_fornecedores_count = 0

        successfully_persisted_fornecedores_count = 0
        failed_persisted_fornecedores_count = 0

        for index, fornecedor_to_update in enumerate(fornecedores_to_update):
            logger.info(f"Updating the fornecedor {index + 1} of {len(fornecedores_to_update)} (CNPJ: {fornecedor_to_update.identificacao.cnpj.value})")
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

            try:
                self.persist_updated_fornecedor(
                    fornecedor,
                    workflow_trace_id,
                    fornecedor_trace_id
                )
                successfully_persisted_fornecedores_count += 1
            except PersistUpdatedFornecedorWorkflowError:
                failed_persisted_fornecedores_count += 1
                continue

        result = GetAndUpdateFornecedoresWorkflowResult(
            trace_id=workflow_trace_id,
            fornecedores_to_update_count=len(fornecedores_to_update),
            successfully_built_fornecedores_count=successfully_built_fornecedores_count,
            failed_built_fornecedores_count=failed_built_fornecedores_count,
            successfully_updated_fornecedores_count=successfully_updated_fornecedores_count,
            failed_updated_fornecedores_count=failed_updated_fornecedores_count,
            successfully_persisted_fornecedores_count=successfully_persisted_fornecedores_count,
            failed_persisted_fornecedores_count=failed_persisted_fornecedores_count,
        )
        self._log_result(result)
        return result
