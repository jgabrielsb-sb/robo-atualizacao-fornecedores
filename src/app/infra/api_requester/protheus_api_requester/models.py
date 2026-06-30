import re
from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TipoOperacaoProtheus(str, Enum):
    INCLUSAO = "3"
    ALTERACAO = "4"


class TipoFornecedorProtheus(str, Enum):
    PESSOA_FISICA = "F"
    PESSOA_JURIDICA = "J"
    ESTRANGEIRO = "X"


class SimNaoProtheus(str, Enum):
    """Used by For_Ativ and Cooperat fields."""
    SIM = "S"
    NAO = "N"


class SimplesNacionalProtheus(str, Enum):
    """Used by Simples field — note: full words, not S/N."""
    SIM = "SIM"
    NAO = "NAO"


class VinculoSebraeProtheus(str, Enum):
    CONSELHEIRO = "C"
    DIRETOR = "D"
    FUNCIONARIO = "F"
    GERENTE = "G"
    ESTAGIARIO = "E"
    SEM_VINCULO = "Z"


class FederacaoProtheus(str, Enum):
    NAO = "0"
    FEDERACAO = "1"
    CONFEDERACAO = "2"


class ClassificacaoProtheus(str, Enum):
    EIRELI = "EI"
    EMPRESA_PUBLICA = "EP"
    EMPRESA_PEQUENO_PORTE = "EPP"
    MICRO_EMPRESA = "ME"
    MEI = "MEI"
    NORMAL = "N"
    PESSOA_FISICA = "PF"
    SEM_FINS_LUCRATIVOS = "SFL"
    DEMAIS = "D"
    NAO_INFORMADO = "NI"

class TipoPessoaProtheus(str, Enum):
    CI = "CI"
    PF = "PF"
    OS = "OS"


class ProtheusUpdateResult(BaseModel):
    codigo_for: str
    loja_forne: str


class BancosProtheus(BaseModel):
    Banco_Fo: str = ""
    Agenc_Fo: str = ""
    Conta_Fo: str = ""

class FornecedorUpdateOnProtheus(BaseModel):
    """
    DTO representing the Protheus INCLUIRFORNECEDOR payload for Tipo_Ope=4 (alteration).
    cAuth and Tipo_Ope are NOT included — the requester injects them at call time.
    """
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)

    # Identification (required for Tipo_Ope=4)
    CNPJ_For: str

    # Name
    Nome_For: str
    Nome_Red: str = ""

    # Address
    Ende_For: str
    Nume_End: str
    Cmpl_End: str = ""
    Bair_For: str
    Esta_For: str = "" # UF sigla, e.g. "AL"
    Codi_Mun: str  # IBGE code
    Muni_For: str
    CEP_Forn: str

    # Contact
    Ema_Forn: str = ""
    DDD_Forn: str = ""
    Tel_Forn: str = ""

    # Classification
    Tipo_Forn: TipoFornecedorProtheus
    Classifi: ClassificacaoProtheus

    # Tax / registration
    Insc_Est: str = ""

    # Status
    For_Ativ: SimNaoProtheus  # "S"/"N"
    Moti_Blq: str = "" # Motivo de bloqueio

    # Fiscal
    Simples: SimplesNacionalProtheus  # "SIM"/"NAO" — different format from S/N fields
    Cod_Rete: str

    # SEBRAE-specific
    Vinc_Seb: VinculoSebraeProtheus
    Federaca: FederacaoProtheus
    Cooperat: SimNaoProtheus  # "S"/"N"

    cTipPess: TipoPessoaProtheus

    # Banks
    Bancos: List[BancosProtheus] = Field(
        default_factory=lambda: [BancosProtheus(Banco_Fo="", Agenc_Fo="", Conta_Fo="")]
    )

    @field_validator("CEP_Forn")
    @classmethod
    def strip_cep_formatting(cls, v: str) -> str:
        return re.sub(r"\D", "", v)

    @field_validator(
        "Nome_Red",
        "Cmpl_End",
        "Ema_Forn",
        "DDD_Forn",
        "Tel_Forn",
        "Insc_Est",
        "Esta_For",
        mode="before",
    )
    @classmethod
    def convert_none_to_empty_string(cls, v: str | None) -> str:
        return "" if v is None else v

    @field_validator("CNPJ_For")
    @classmethod
    def strip_cnpj_formatting(cls, v: str) -> str:
        return re.sub(r"\D", "", v)
