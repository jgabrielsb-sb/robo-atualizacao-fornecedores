from datetime import datetime, timezone
from typing import Optional

from app.application.ports import (
    GetUpdatedFornecedoresToSendToPPEPort,
    SendUpdatedFornecedorToPPEPort,
    SendUpdatedFornecedorToPPERepositoryPort,
)
from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)


def make_fake_atualizacao_fornecedor(id: int) -> PersistUpdatedFornecedorResult:
    now = datetime.now(timezone.utc)
    return PersistUpdatedFornecedorResult(
        id=id,
        cnpj=f"{id:014d}",
        step_update_on_ppe_attempt_count=0,
        step_update_on_ppe_status_id=1,
        created_at=now,
        updated_at=now,
    )


class FakeGetUpdatedFornecedoresToSendToPPEPort(GetUpdatedFornecedoresToSendToPPEPort):
    def __init__(
        self,
        atualizacoes_fornecedores: list[PersistUpdatedFornecedorResult] | None = None,
        error: Exception | None = None,
    ):
        self.atualizacoes_fornecedores = atualizacoes_fornecedores or []
        self.error = error

    def get(self) -> list[PersistUpdatedFornecedorResult]:
        if self.error:
            raise self.error
        return self.atualizacoes_fornecedores


class FakeSendUpdatedFornecedorToPPEPort(SendUpdatedFornecedorToPPEPort):
    def __init__(self, fail_fornecedores_ids: list[int] | None = None):
        self._fail_fornecedores_ids = fail_fornecedores_ids or []
        self.calls: list[PersistUpdatedFornecedorResult] = []

    def send(self, atualizacao_fornecedor: PersistUpdatedFornecedorResult):
        self.calls.append(atualizacao_fornecedor)
        if atualizacao_fornecedor.id in self._fail_fornecedores_ids:
            raise RuntimeError("Error sending updated fornecedor to PPE")
        return {"sent": True}


class FakeSendUpdatedFornecedorToPPERepositoryPort(SendUpdatedFornecedorToPPERepositoryPort):
    def __init__(self, fail_fornecedores_ids: list[int] | None = None):
        self._fail_fornecedores_ids = fail_fornecedores_ids or []
        self.calls: list[tuple[PersistUpdatedFornecedorResult, Optional[str]]] = []

    def save(
        self,
        atualizacao_fornecedor: PersistUpdatedFornecedorResult,
        why_error: Optional[str] = None,
    ) -> PersistUpdatedFornecedorResult:
        self.calls.append((atualizacao_fornecedor, why_error))
        if atualizacao_fornecedor.id in self._fail_fornecedores_ids:
            raise RuntimeError("Error registering update_on_ppe attempt")
        return atualizacao_fornecedor
