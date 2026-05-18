from pydantic import BaseModel

from app.application.ports import (
    GetCNPJsToUpdatePort,
    BuildFornecedorPort,
    UpdateFornecedorPort,
)
from app.domain.value_objects import CNPJ


def make_fake_cnpj(id: int) -> CNPJ:
    return CNPJ(value=f"{id:014d}")


class FakeFornecedor(BaseModel):
    id: int

    def __str__(self) -> str:
        return f"Fornecedor(id={self.id})"


class FakeGetCNPJsToUpdatePort(GetCNPJsToUpdatePort):
    def __init__(
        self,
        cnpjs: list[CNPJ] | None = None,
        error: Exception | None = None,
    ):
        self.cnpjs = cnpjs or []
        self.error = error

    def get(self) -> list[CNPJ]:
        if self.error:
            raise self.error
        return self.cnpjs


class FakeBuildFornecedorPort(BuildFornecedorPort):
    def __init__(self, fail_fornecedores_ids: list[int] | None = None):
        self._fail_fornecedores_ids = fail_fornecedores_ids or []

    def build(self, cnpj: CNPJ) -> FakeFornecedor:
        id_ = int(cnpj.value)
        if id_ in self._fail_fornecedores_ids:
            raise RuntimeError("Error building fornecedor")
        return FakeFornecedor(id=id_)


class FakeUpdateFornecedorPort(UpdateFornecedorPort):
    def __init__(self, fail_fornecedores_ids: list[int] | None = None):
        self._fail_fornecedores_ids = fail_fornecedores_ids or []

    def update(self, fornecedor: FakeFornecedor):
        if fornecedor.id in self._fail_fornecedores_ids:
            raise RuntimeError("Error updating fornecedor")
        return fornecedor
