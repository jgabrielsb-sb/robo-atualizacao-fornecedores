from abc import ABC, abstractmethod

from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)


class GetUpdatedFornecedoresToSendToPPEPort(ABC):
    @abstractmethod
    def get(self) -> list[PersistUpdatedFornecedorResult]:
        pass
