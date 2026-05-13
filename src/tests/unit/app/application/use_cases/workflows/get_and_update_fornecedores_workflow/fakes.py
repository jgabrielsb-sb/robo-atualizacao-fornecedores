from pydantic import BaseModel

from app.application.ports import (
    GetFornecedoresToUpdatePort,
    BuildFornecedorPort,
    FornecedorRepositoryPort,
)
from app.domain.value_objects import CNPJ


class FakeFornecedorToUpdate(BaseModel):
    id: int

    @property
    def cnpj(self) -> CNPJ:
        return CNPJ(value=f"{self.id:014d}")

    def __str__(self) -> str:
        return f"FornecedorToUpdate(id={self.id})"


class FakeFornecedor(BaseModel):
    id: int

    def __str__(self) -> str:
        return f"Fornecedor(id={self.id})"


class FakeGetFornecedoresToUpdatePort(GetFornecedoresToUpdatePort):
    def __init__(
        self,
        fornecedores: list[FakeFornecedorToUpdate] | None = None,
        error: Exception | None = None,
    ):
        self.fornecedores = fornecedores or []
        self.error = error

    def get(self):
        if self.error:
            raise self.error
        return self.fornecedores


class FakeBuildFornecedorPort(BuildFornecedorPort):
    def __init__(self, fail_fornecedores_ids: list[int] | None = None):
        self._fail_fornecedores_ids = fail_fornecedores_ids or []

    def build(self, cnpj: CNPJ) -> FakeFornecedor:
        id_ = int(cnpj.value)
        if id_ in self._fail_fornecedores_ids:
            raise RuntimeError("Error building fornecedor")
        return FakeFornecedor(id=id_)


class FakeFornecedorRepositoryPort(FornecedorRepositoryPort):
    def __init__(self, fail_fornecedores_ids: list[int] | None = None):
        self._fail_fornecedores_ids = fail_fornecedores_ids or []

    def create(self):
        pass

    def update(self, fornecedor: FakeFornecedor):
        if fornecedor.id in self._fail_fornecedores_ids:
            raise RuntimeError("Error updating fornecedor")
        return fornecedor
