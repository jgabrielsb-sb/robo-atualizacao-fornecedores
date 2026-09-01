"""
Workflow responsible for retrieving the atualizacoes_fornecedores pending
the update_on_ppe stage, sending each one to PPE, and registering the
attempt (success or failure) back on the API.
"""
import logging
import uuid
from typing import Optional

from pydantic import BaseModel

from app.domain.enums import StatusEnum

from app.application.ports import (
    GetUpdatedFornecedoresToSendToPPEPort,
    SendUpdatedFornecedorToPPEPort,
    SendUpdatedFornecedorToPPERepositoryPort,
)
from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)

logger = logging.getLogger(__name__)

class SendUpdatedFornecedoresToPPEWorkflowError(Exception):
    pass

class GetUpdatedFornecedoresToSendToPPEWorkflowError(SendUpdatedFornecedoresToPPEWorkflowError):
    pass

class SendUpdatedFornecedorToPPEWorkflowError(SendUpdatedFornecedoresToPPEWorkflowError):
    pass

class RegisterUpdateOnPPEAttemptWorkflowError(SendUpdatedFornecedoresToPPEWorkflowError):
    pass


class SendUpdatedFornecedoresToPPEWorkflowResult(BaseModel):
    trace_id: str
    fornecedores_to_send_count: int
    successfully_sent_fornecedores_count: int
    failed_sent_fornecedores_count: int
    successfully_registered_fornecedores_count: int
    failed_registered_fornecedores_count: int


GET_UPDATED_FORNECEDORES_TO_SEND_TO_PPE_EVENT_NAME = "GET_UPDATED_FORNECEDORES_TO_SEND_TO_PPE"
SEND_UPDATED_FORNECEDOR_TO_PPE_EVENT_NAME = "SEND_UPDATED_FORNECEDOR_TO_PPE"
REGISTER_UPDATE_ON_PPE_ATTEMPT_EVENT_NAME = "REGISTER_UPDATE_ON_PPE_ATTEMPT"
WORKFLOW_EVENT_NAME = "SEND_UPDATED_FORNECEDORES_TO_PPE"

class SendUpdatedFornecedoresToPPEWorkflow:
    def __init__(
        self,
        get_updated_fornecedores_to_send_to_ppe: GetUpdatedFornecedoresToSendToPPEPort,
        send_updated_fornecedor_to_ppe: SendUpdatedFornecedorToPPEPort,
        send_updated_fornecedor_to_ppe_repository: SendUpdatedFornecedorToPPERepositoryPort,
    ):
        self._get_updated_fornecedores_to_send_to_ppe = get_updated_fornecedores_to_send_to_ppe
        self._send_updated_fornecedor_to_ppe = send_updated_fornecedor_to_ppe
        self._send_updated_fornecedor_to_ppe_repository = send_updated_fornecedor_to_ppe_repository

    def get_updated_fornecedores_to_send_to_ppe(
        self,
        workflow_trace_id: str,
    ) -> list[PersistUpdatedFornecedorResult]:
        trace_id = str(uuid.uuid4())
        EVENT_NAME = GET_UPDATED_FORNECEDORES_TO_SEND_TO_PPE_EVENT_NAME
        try:
            atualizacoes_fornecedores = self._get_updated_fornecedores_to_send_to_ppe.get()
            logger.info(
                "Successfully retrieved updated fornecedores to send to PPE",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "count": len(atualizacoes_fornecedores),
                    "output": [atualizacao_fornecedor.cnpj for atualizacao_fornecedor in atualizacoes_fornecedores],
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                }
            )
            return atualizacoes_fornecedores
        except Exception as e:
            logger.error(
                "Failed to retrieve updated fornecedores to send to PPE",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                },
                exc_info=True,
            )
            raise GetUpdatedFornecedoresToSendToPPEWorkflowError(
                f"Failed to retrieve updated fornecedores to send to PPE: {e}"
            ) from e

    def send_updated_fornecedor_to_ppe(
        self,
        atualizacao_fornecedor: PersistUpdatedFornecedorResult,
        workflow_trace_id: str,
        fornecedor_trace_id: str,
    ) -> None:
        trace_id = str(uuid.uuid4())
        EVENT_NAME = SEND_UPDATED_FORNECEDOR_TO_PPE_EVENT_NAME
        try:
            result = self._send_updated_fornecedor_to_ppe.send(atualizacao_fornecedor)
            logger.info(
                "Successfully sent updated fornecedor to PPE",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": atualizacao_fornecedor.cnpj,
                    "input": atualizacao_fornecedor.model_dump(mode="json"),
                    "output": result,
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                }
            )
        except Exception as e:
            logger.error(
                "Failed to send updated fornecedor to PPE",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": atualizacao_fornecedor.cnpj,
                    "input": atualizacao_fornecedor.model_dump(mode="json"),
                    "output": None,
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                },
                exc_info=True,
            )
            raise SendUpdatedFornecedorToPPEWorkflowError(
                f"Failed to send updated fornecedor to PPE: {e}"
            ) from e

    def register_update_on_ppe_attempt(
        self,
        atualizacao_fornecedor: PersistUpdatedFornecedorResult,
        why_error: Optional[str],
        workflow_trace_id: str,
        fornecedor_trace_id: str,
    ) -> None:
        trace_id = str(uuid.uuid4())
        EVENT_NAME = REGISTER_UPDATE_ON_PPE_ATTEMPT_EVENT_NAME
        try:
            result = self._send_updated_fornecedor_to_ppe_repository.save(
                atualizacao_fornecedor, why_error=why_error
            )
            logger.info(
                "Successfully registered update_on_ppe attempt",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": atualizacao_fornecedor.cnpj,
                    "input": {"id": atualizacao_fornecedor.id, "why_error": why_error},
                    "output": result.model_dump(mode="json"),
                    "status": StatusEnum.SUCCESS.value,
                    "event_name": EVENT_NAME,
                }
            )
        except Exception as e:
            logger.error(
                "Failed to register update_on_ppe attempt",
                extra={
                    "trace_id": trace_id,
                    "workflow_trace_id": workflow_trace_id,
                    "fornecedor_trace_id": fornecedor_trace_id,
                    "fornecedor_cnpj": atualizacao_fornecedor.cnpj,
                    "input": {"id": atualizacao_fornecedor.id, "why_error": why_error},
                    "output": None,
                    "status": StatusEnum.ERROR.value,
                    "event_name": EVENT_NAME,
                },
                exc_info=True,
            )
            raise RegisterUpdateOnPPEAttemptWorkflowError(
                f"Failed to register update_on_ppe attempt: {e}"
            ) from e

    def _process_atualizacao_fornecedor(
        self,
        atualizacao_fornecedor: PersistUpdatedFornecedorResult,
        workflow_trace_id: str,
    ) -> tuple[bool, bool]:
        fornecedor_trace_id = str(uuid.uuid4())

        why_error: Optional[str] = None
        sent_successfully = True
        try:
            self.send_updated_fornecedor_to_ppe(
                atualizacao_fornecedor, workflow_trace_id, fornecedor_trace_id
            )
        except SendUpdatedFornecedorToPPEWorkflowError as e:
            sent_successfully = False
            why_error = str(e)

        # The attempt must be registered regardless of whether sending to PPE
        # succeeded or failed: either way the API needs the outcome recorded.
        registered_successfully = True
        try:
            self.register_update_on_ppe_attempt(
                atualizacao_fornecedor, why_error, workflow_trace_id, fornecedor_trace_id
            )
        except RegisterUpdateOnPPEAttemptWorkflowError:
            registered_successfully = False

        return sent_successfully, registered_successfully

    def _log_result(
        self,
        result: SendUpdatedFornecedoresToPPEWorkflowResult,
    ) -> None:
        all_succeeded = (
            result.failed_sent_fornecedores_count == 0
            and result.failed_registered_fornecedores_count == 0
        )

        status = StatusEnum.SUCCESS.value if all_succeeded else StatusEnum.WARNING.value
        message = "Successfully sent all updated fornecedores to PPE" if all_succeeded else "Failed to send some updated fornecedores to PPE"
        log_method = logger.info if all_succeeded else logger.warning

        log_method(
            message,
            extra={
                "trace_id": result.trace_id,
                "status": status,
                "event_name": WORKFLOW_EVENT_NAME,
                "fornecedores_to_send_count": result.fornecedores_to_send_count,
                "successfully_sent_fornecedores_count": result.successfully_sent_fornecedores_count,
                "failed_sent_fornecedores_count": result.failed_sent_fornecedores_count,
                "successfully_registered_fornecedores_count": result.successfully_registered_fornecedores_count,
                "failed_registered_fornecedores_count": result.failed_registered_fornecedores_count,
            },
        )

    def run(self) -> SendUpdatedFornecedoresToPPEWorkflowResult:
        workflow_trace_id = str(uuid.uuid4())

        atualizacoes_fornecedores = self.get_updated_fornecedores_to_send_to_ppe(workflow_trace_id)

        successfully_sent_fornecedores_count = 0
        failed_sent_fornecedores_count = 0

        successfully_registered_fornecedores_count = 0
        failed_registered_fornecedores_count = 0

        for atualizacao_fornecedor in atualizacoes_fornecedores:
            sent_successfully, registered_successfully = self._process_atualizacao_fornecedor(
                atualizacao_fornecedor, workflow_trace_id
            )

            if sent_successfully:
                successfully_sent_fornecedores_count += 1
            else:
                failed_sent_fornecedores_count += 1

            if registered_successfully:
                successfully_registered_fornecedores_count += 1
            else:
                failed_registered_fornecedores_count += 1

        result = SendUpdatedFornecedoresToPPEWorkflowResult(
            trace_id=workflow_trace_id,
            fornecedores_to_send_count=len(atualizacoes_fornecedores),
            successfully_sent_fornecedores_count=successfully_sent_fornecedores_count,
            failed_sent_fornecedores_count=failed_sent_fornecedores_count,
            successfully_registered_fornecedores_count=successfully_registered_fornecedores_count,
            failed_registered_fornecedores_count=failed_registered_fornecedores_count,
        )
        self._log_result(result)
        return result
