import logging

from app.infra.api_requester.fornecedores_api_requester import FornecedoresAPIRequester
from app.domain.value_objects import (
    CNPJ, 
    InvalidCNPJError, 
    CPF, 
    InvalidCPFError,
)
from app.application.ports import GetCNPJsToUpdatePort

logger = logging.getLogger(__name__)

class GetCNPJsToUpdateViaFornecedoresAPIError(Exception):
    pass

class InvalidIdentifierError(GetCNPJsToUpdateViaFornecedoresAPIError):
    pass

class GetCNPJsToUpdateViaFornecedoresAPI(GetCNPJsToUpdatePort):
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
            if self._is_cpf(fornecedor.CPF_CNPJ):
                continue

            try:
                cnpj = CNPJ.create(cnpj=fornecedor.CPF_CNPJ)
                cnpjs.append(cnpj)
            except InvalidCNPJError:
                #logger.warning(f"The identifier {fornecedor.CPF_CNPJ} is not a valid CNPJ nor a valid CPF")
                pass

        return cnpjs
