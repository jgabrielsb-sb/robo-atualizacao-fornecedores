from abc import ABC, abstractmethod
from typing import Any

from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)


class SendUpdatedFornecedorToPPEPort(ABC):
    @abstractmethod
    def send(self, atualizacao_fornecedor: PersistUpdatedFornecedorResult) -> Any:
        pass
