from pydantic import BaseModel

from app.application.ports import (
    FornecedorToUpdateRepositoryPort, 
    GetFornecedoresToUpdatePort
)


class FakeFornecedorToUpdate(BaseModel):
    id: int

    def __str__(self)-> str:
        return f"FornecedorToUpdate(id_fornecedor={self.id})"


class FakeGetFornecedoresToUpdate(GetFornecedoresToUpdatePort):
    def __init__(
        self, 
        fornecedores: list[FakeFornecedorToUpdate] | None = None, 
        error: Exception | None = None
    ):
        self.fornecedores = fornecedores or []
        self.error = error
        self.called = False

    def get(self):
        self.called = True

        if self.error:
            raise self.error

        return self.fornecedores


class SpyFornecedorToUpdateRepository(FornecedorToUpdateRepositoryPort):
    def __init__(self, fail_fornecedores: list[FakeFornecedorToUpdate] | None = None):
        self.saved_fornecedores = []
        self.fail_fornecedores = fail_fornecedores or set()

    def save(self, fornecedor: FakeFornecedorToUpdate):
        if fornecedor.id in [fail_fornecedor.id for fail_fornecedor in self.fail_fornecedores]:
            print(f"Failed to save fornecedor: {fornecedor}")
            raise RuntimeError("Database error")

        self.saved_fornecedores.append(fornecedor)

        return fornecedor