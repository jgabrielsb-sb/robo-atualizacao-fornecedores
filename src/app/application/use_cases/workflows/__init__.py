from dataclasses import dataclass


@dataclass
class WorkflowAtualizacaoFornecedoresUseCase:
    fornecedor_repository: object
    receita_federal: object
    event_dispatcher: object

    def execute(self) -> None:
        raise NotImplementedError
