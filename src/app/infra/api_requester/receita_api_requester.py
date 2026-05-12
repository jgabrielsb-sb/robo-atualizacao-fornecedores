import requests
from http import HTTPStatus
from pydantic import BaseModel
from typing import Optional

from app.infra.api_requester import RouteNotFoundError, NotFoundError, UnexpectedError
from app.domain.value_objects import CNPJ

class ReceitaAPIGetCompanyResponse(BaseModel):
    CNPJ: Optional[str] = None  
    NOME_EMPRESARIAL: Optional[str] = None
    NOME_FANTASIA: Optional[str] = None
    SIT_CADASTAL: Optional[str] = None
    MOT_SIT_CADASTAL: Optional[str] = None
    DT_SIT_CADASTAL: Optional[int] = None
    DT_ABERTURA_ESTAB: Optional[int] = None
    CNAE_PRINCIPAL_COD: Optional[str] = None
    END_UF: Optional[str] = None
    OPCAO_MEI: Optional[str] = None
    PORTE: Optional[str] = None
    LISTA_QSA_SOCIO_NOME: Optional[str] = None
    END_TIPO_LOGRADOURO: Optional[str] = None
    END_LOGRADOURO: Optional[str] = None
    END_NUMERO: Optional[str] = None
    END_COMPLEMENTO: Optional[str] = None   
    END_BAIRRO: Optional[str] = None
    END_CEP: Optional[str] = None
    END_MUNICIPIO: Optional[str] = None
    DDD1: Optional[str] = None
    TELEFONE1: Optional[str] = None
    DDD2: Optional[str] = None
    TELEFONE2: Optional[str] = None
    EMAIL: Optional[str] = None
    RESPONSAVEL_CPF: Optional[str] = None
    RESPONSAVEL_NOME: Optional[str] = None
    HASH: Optional[str] = None

class ReceitaAPIRequester:
    def __init__(
        self,
        base_url: str,
    ):
        self._base_url = base_url

    def get_company(
        self,
        cnpj: CNPJ
    ) -> ReceitaAPIGetCompanyResponse:
        """
        Gets the company by cnpj using the Receita API.

        :param cnpj: The cnpj of the company.
        :type cnpj: CNPJ
        :return: The company.
        :rtype: ReceitaAPIGetCompanyResponse
        :raises RouteNotFoundError: If the route is not found.
        :raises NotFoundError: If the company is not found.
        :raises UnexpectedError: If an unexpected error occurs.
        """
        url = f"{self._base_url}/receita/api/v1/empresa-receita/get-by-cnpj/{cnpj.value}"
        response = requests.get(url)
    
        if response.status_code == HTTPStatus.OK:
            data = response.json()
            return ReceitaAPIGetCompanyResponse.model_validate(data)
        
        elif response.status_code == HTTPStatus.NOT_FOUND:
            if response.json().get("detail") and "Not Found" in response.json().get("detail"):
                raise RouteNotFoundError(
                    f"Route not found: {url}"
                )
            
            raise NotFoundError(
                f"Company not found: {cnpj.value}. API Response: {response.json()}"
            )
        
        else:
            raise UnexpectedError(
                f"Unexpected error: {response.json()}. API Response: {response.json()}"
            )