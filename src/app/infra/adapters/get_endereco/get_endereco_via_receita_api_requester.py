
from app.domain.value_objects import CNPJ, Endereco, CEP, Municipio
from app.infra.api_requester import ReceitaAPIRequester
from app.application.ports import (
    GetEnderecoPort, 
    MunicipioLookupPort,
)

class ErrorWhileGettingExternalDataError(Exception):
    pass

class GetEnderecoViaReceitaAPIRequester(GetEnderecoPort):
    def __init__(
        self, 
        municipio_lookup_port: MunicipioLookupPort, 
        receita_api_requester: ReceitaAPIRequester,
    ):
        self._municipio_lookup_port = municipio_lookup_port
        self._receita_api_requester = receita_api_requester

    def _get_municipio(self, municipio_name: str) -> Municipio:
        try:
            return self._municipio_lookup_port.get(municipio_name)
        except Exception as e:
            raise ErrorWhileGettingExternalDataError(
                f"Failed to get municipio -- {municipio_name} -- : {e}"
            ) from e

    def get(self, cnpj: CNPJ) -> Endereco:
        response = self._receita_api_requester.get_company(cnpj)
        return Endereco.create(
            endereco=response.END_LOGRADOURO,
            numero=response.END_NUMERO,
            complemento=response.END_COMPLEMENTO,
            cep=CEP.create(cep=response.END_CEP) if response.END_CEP else None,
            municipio=self._get_municipio(response.END_MUNICIPIO) if response.END_MUNICIPIO else None,
        )