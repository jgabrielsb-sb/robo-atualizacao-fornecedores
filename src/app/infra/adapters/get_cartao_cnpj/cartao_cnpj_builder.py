from enum import Enum
from typing import Any, Dict


from app.domain.enums import PorteEnum
from app.application.ports import MunicipioLookupPort
from app.domain.enums import SituacaoCadastralEnum
from app.infra.adapters.exceptions import ErrorWhileGettingExternalDataError

from app.domain.value_objects import (
    Endereco, 
    Municipio,
    CEP,
    CartaoCNPJ,
    Telefone,
)


map_porte = {
    "ME": PorteEnum.ME,
    "EPP": PorteEnum.EPP,
    "EIRELI": PorteEnum.EIRELI,
    "EP": PorteEnum.EP,
    "N": PorteEnum.N,
    "PF": PorteEnum.PF,
    "SFL": PorteEnum.SFL,
    "DEMAIS": PorteEnum.D,
    "MEI": PorteEnum.MEI,
}

def _map_porte(size: str) -> PorteEnum:
    porte_enum = map_porte.get(size)
    if not porte_enum:
        raise ValueError(f"Could not map porte to a valid PorteEnum: {size}")
    return porte_enum

class CartaoCNPJBuilder:
    def __init__(
        self,
        municipio_lookup_port: MunicipioLookupPort,
    ):
        self._municipio_lookup_port = municipio_lookup_port

    def _get_municipio(self, municipio_name: str) -> Municipio:
        try:
            return self._municipio_lookup_port.get(municipio_name)
        except Exception as e:
            raise ErrorWhileGettingExternalDataError(f"Failed to get municipio: {e}") from e

    def _get_endereco(self, address: Dict[str, Any]) -> Endereco:
        cep = CEP.create(cep=address["zip_code"]) if address["zip_code"] else None
        municipio = self._get_municipio(address["city"]) if address["city"] else None
        
        return Endereco.create(
            endereco=address["street"],
            numero=address["number"],
            complemento=address["complement"],
            cep=cep,
            municipio=municipio,
        )

    def _get_telefone(self, telefone: str) -> Telefone:
        if "/" in telefone:
            telefone = telefone.split("/")[0]

        return Telefone.create(
            value=telefone
        )

    def _get_situacao_cadastral(self, situacao_cadastral: str) -> SituacaoCadastralEnum:
        return SituacaoCadastralEnum.from_value(situacao_cadastral)

    def build(self, response: Dict[str, Any]) -> CartaoCNPJ:
        data = response["data"]
        return CartaoCNPJ(
            porte=_map_porte(data["size"]),
            razao_social=data["legal_name"],
            nome_fantasia=data["trade_name"],
            atividade_economica_principal_str=data["primary_activity"]["description"],
            endereco=self._get_endereco(data["address"]),
            telefone=self._get_telefone(data["contact"]["phone"]) ,
            natureza_juridica=data["legal_nature"]["description"],
            situacao_cadastral=self._get_situacao_cadastral(data["registration_status"]["status"]), 
        )