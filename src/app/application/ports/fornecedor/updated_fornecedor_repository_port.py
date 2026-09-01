from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.value_objects import CNPJ


class PersistUpdatedFornecedorResult(BaseModel):
    id: int
    cnpj: str
    step_update_on_ppe_last_attempted_at: Optional[datetime] = None
    step_update_on_ppe_last_error_message: Optional[str] = None
    step_update_on_ppe_attempt_count: int
    step_update_on_ppe_status_id: int
    created_at: datetime
    updated_at: datetime


class UpdatedFornecedorRepositoryPort(ABC):
    @abstractmethod
    def create(self, cnpj: CNPJ) -> PersistUpdatedFornecedorResult:
        pass
