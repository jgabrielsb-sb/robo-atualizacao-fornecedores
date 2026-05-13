from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester
from app.domain.value_objects import (
    CNPJ, 
    InvalidCNPJError, 
    CPF, 
    InvalidCPFError,
)

class InvalidIdentifierError(Exception):
    pass

class GetCNPJsToUpdateViaFornecedoresAPIRequester:
    def __init__(
        self,
        fornecedores_api_requester: FornecedoresAPIRequester,
    ):
        self._fornecedores_api_requester = fornecedores_api_requester

    def _is_cpf(self, cpf_value: str) -> bool:
        try:
            CPF.create(cpf=cpf_value)
            return True
        except InvalidCPFError:
            return False

    def get(self) -> list[CNPJ]:
        """
        Get the CNPJs to update from the Fornecedores API Requester.
        Returns:
            list[CNPJ]: The CNPJs to update.
        """
        cnpjs = []
        fornecedores_to_update = self._fornecedores_api_requester.get_fornecedores_to_update() or []
        
        for fornecedor in fornecedores_to_update:
            if self._is_cpf(fornecedor.cpf_cnpj):
                continue

            try:
                cnpj = CNPJ.create(cnpj=fornecedor.cpf_cnpj)
                cnpjs.append(cnpj)
            except InvalidCNPJError:
                raise InvalidIdentifierError(
                    f"The identifier {fornecedor.cpf_cnpj} is not a valid CNPJ nor a valid CPF"
                )

        return cnpjs
