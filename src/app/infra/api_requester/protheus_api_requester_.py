
from pydantic import BaseModel
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import requests

from app.domain.enums import (
    PorteEnum, 
    TipoPessoaEnum,
    VinculoSebraeEnum
)
from app.domain.value_objects import CodigoMunicipioIBGE, Municipio, DDD

class TipoOperacaoEnum(str, Enum):
    ALTERACAO = "4"
    INCLUSAO = "3"

@dataclass
class FornecedorToUpdate:
    opt_simples_nacional: bool
    razao_social: str
    
    porte: PorteEnum
    logradouro: str
    numero: str
    bairro: str
    municipio: Municipio
    ddd: DDD
    ativo: bool
    bloqueado: bool
    tipo_pessoa: TipoPessoaEnum
    vinculo_sebrae: VinculoSebraeEnum
    cooperativa: bool
    codigo_retencao: str
    nome_fantasia: Optional[str] = None
    complemento: Optional[str] = None
    motivo_bloqueio: Optional[str] = None

    @classmethod
    def create(
        cls,
        *,
        opt_simples_nacional: bool,
        razao_social: str,
        porte: PorteEnum,
        logradouro: str,
        numero: str,
        bairro: str,
        municipio: Municipio,
        ddd: DDD,
        ativo: bool,
        bloqueado: bool,
        tipo_pessoa: TipoPessoaEnum,
        vinculo_sebrae: VinculoSebraeEnum,
        cooperativa: bool,
        codigo_retencao: str,
        nome_fantasia: Optional[str] = None,
        complemento: Optional[str] = None,
        motivo_bloqueio: Optional[str] = None,
    ) -> 'FornecedorToUpdate':
        return cls(
            opt_simples_nacional=opt_simples_nacional,
            razao_social=razao_social,
            nome_fantasia=nome_fantasia,
            porte=porte,
            logradouro=logradouro,
            numero=numero,
            bairro=bairro,
            municipio=municipio,
            ddd=ddd,
            ativo=ativo,
            bloqueado=bloqueado,
            tipo_pessoa=tipo_pessoa,
            vinculo_sebrae=vinculo_sebrae,
            cooperativa=cooperativa,
            codigo_retencao=codigo_retencao,
            complemento=complemento,
            motivo_bloqueio=motivo_bloqueio,
        )

    def to_json(self) -> dict:
        dipara_porte = {
            PorteEnum.EIRELI: "EI",
            PorteEnum.EP: "EP",
            PorteEnum.EPP: "EPP",
            PorteEnum.ME: "ME",
            PorteEnum.MEI: "MEI",
            PorteEnum.N: "N",
            PorteEnum.PF: "PF",
            PorteEnum.SFL: "SFL",
            PorteEnum.D: "D",
        }

        dipara_vinculo_sebrae = {
            VinculoSebraeEnum.Z: "Z",
        }

        return {
           
            "Nome_For": self.razao_social,
            "Nome_Red": self.nome_fantasia,
            "Classifi": dipara_porte[self.porte],
            "Ende_For": self.logradouro,
            "Nume_End": self.numero,
            "Cmpl_End": self.complemento,
            "Bair_For": self.bairro,
            "Codi_Mun": self.municipio.codigo_ibge.value,
            "Muni_For": self.municipio.nome,
            "DDD_Tele": self.ddd.value,
            "Simples": "SIM" if self.opt_simples_nacional else "NAO",
            "For_Ativ": "SIM" if self.ativo else "NAO",
            "Coop_For": "S" if self.cooperativa else "N",
            "Bloq_For": self.bloqueado,
            "Moti_Blq": self.motivo_bloqueio,
            "Vinc_Seb": dipara_vinculo_sebrae[self.vinculo_sebrae],
            "Cod_Rete": self.codigo_retencao,
        }
    
    

class ProtheusAPIRequester:
    def __init__(
        self,
        base_url: str,
        cAuth: str,
        authorization_token: str,
    ):
        self._base_url = base_url
        self._cAuth = cAuth
        self._authorization_token = authorization_token
        self._headers = {
            "Authorization": f"BASIC {self._authorization_token}"
        }

    def update_fornecedor(
        self, 
        fornecedor: FornecedorToUpdate
    ):
        url = f"{self._base_url}/REST/APIPROTHEUSDB/INCLUIRFORNECEDOR"
        
        data = fornecedor.to_json()
        data.update({
            "cAuth": CAUTH
        })
        
        response = requests.post(
            url, 
            headers=self._headers, 
            json=data,
            timeout=10
        )
        
        print(response.json())