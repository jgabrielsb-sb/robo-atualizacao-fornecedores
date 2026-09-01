from abc import ABC, abstractmethod
from typing import Optional

from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)


class SendUpdatedFornecedorToPPERepositoryPort(ABC):
    @abstractmethod
    def save(
        self,
        atualizacao_fornecedor: PersistUpdatedFornecedorResult,
        why_error: Optional[str] = None,
    ) -> PersistUpdatedFornecedorResult:
        pass
