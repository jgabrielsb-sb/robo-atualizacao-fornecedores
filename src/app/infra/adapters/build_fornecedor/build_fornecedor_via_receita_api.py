from app.application.ports import (
    BuildFornecedorPort,
    MunicipioLookupPort,
    GetOptSimplesNacionalPort,
    GetAtividadeEconomicaDescriptionPort,
)
from app.infra.api_requester.receita_api_requester import (
    ReceitaAPIRequester, 
    ReceitaAPIGetCompanyResponse
)

from app.domain import (
    CNPJ, 
    Fornecedor, 
    Endereco, 
    CEP, 
    Municipio,
    FornecedorIdentificacao, 
    FornecedorDadosCadastrais, 
    FornecedorDadosContato,
    PorteEnum,
    SituacaoCadastralEnum,
    TipoPessoaEnum,
    VinculoSebraeEnum,
    FederacaoEnum,
    DDD,
)

from pydantic import BaseModel
from app.utils.normalize_str import normalize_str


class BuildFornecedorViaReceitaAPIError(Exception):
    pass

class GetReceitaAPICompanyResponseError(BuildFornecedorViaReceitaAPIError):
    pass

class GetMunicipioError(BuildFornecedorViaReceitaAPIError):
    pass

class GetOptSimplesNacionalError(BuildFornecedorViaReceitaAPIError):
    pass

class GetAtividadeEconomicaDescriptionError(BuildFornecedorViaReceitaAPIError):
    pass

class BuildFornecedorViaReceitaAPI(BuildFornecedorPort):
    def __init__(
        self, 
        get_opt_simples_nacional_port: GetOptSimplesNacionalPort,
        get_atividade_economica_description_port: GetAtividadeEconomicaDescriptionPort,
        municipio_lookup_port: MunicipioLookupPort,
        receita_api_requester: ReceitaAPIRequester,
    ):
        self._get_opt_simples_nacional_port = get_opt_simples_nacional_port
        self._get_atividade_economica_description_port = get_atividade_economica_description_port
        self._municipio_lookup_port = municipio_lookup_port
        self._receita_api_requester = receita_api_requester

        self._atividade_economica_description = None

    def _get_atividade_economica_description(self, atividade_economica_code: str) -> str:
        try:
            return self._get_atividade_economica_description_port.get(atividade_economica_code)
        except Exception as e:
            raise GetAtividadeEconomicaDescriptionError(
                f"Failed to get atividade economica description -- {atividade_economica_code} -- : {e}"
            ) from e

    def get_receita_api_company(self, cnpj: CNPJ) -> ReceitaAPIGetCompanyResponse:
        try:
            return self._receita_api_requester.get_company(cnpj)
        except Exception as e:
            raise GetReceitaAPICompanyResponseError(
                f"Failed to get receita api company response -- {cnpj} -- : {e}"
            ) from e

    def get_municipio(self, municipio_name) -> Municipio:
        try:
            return self._municipio_lookup_port.get(municipio_name)
        except Exception as e:
            raise GetMunicipioError(
                f"Failed to get municipio -- {municipio_name} -- : {e}"
            ) from e

    def get_porte(self, porte: str) -> PorteEnum | None:
        """
        CÓDIGO DO PORTE DA EMPRESA:
        00 – NÃO INFORMADO
        01 - MICRO EMPRESA
        03 - EMPRESA DE PEQUENO PORTE
        05 - DEMAIS
        """
        if porte == "00":
            return None
        elif porte == "01":
            return PorteEnum.ME
        elif porte == "03":
            return PorteEnum.EPP
        elif porte == "05":
            return PorteEnum.D
        else:
            raise ValueError(
                f"Invalid porte -- {porte} --"
                "Expected values: 00, 01, 03, 05"
            )
    
    def get_opt_simples_nacional(self, cnpj: CNPJ) -> bool:
        try:
            return self._get_opt_simples_nacional_port.get(cnpj)
        except Exception as e:
            raise GetOptSimplesNacionalError(
                f"Failed to get opt simples nacional -- {cnpj} -- : {e}"
            ) from e

    def get_situacao_cadastral(
        self, 
        situacao_cadastral: str
    ) -> SituacaoCadastralEnum:
        """
        CÓDIGO DA SITUAÇÃO CADASTRAL:
        01 – NULA
        2 – ATIVA
        3 – SUSPENSA
        4 – INAPTA
        08 – BAIXADA
        """ 
        if situacao_cadastral == "01":
            return SituacaoCadastralEnum.NULA
        elif situacao_cadastral == "02":
            return SituacaoCadastralEnum.ATIVA
        elif situacao_cadastral == "03":
            return SituacaoCadastralEnum.SUSPENSA
        elif situacao_cadastral == "04":
            return SituacaoCadastralEnum.INAPTA
        elif situacao_cadastral == "08":
            return SituacaoCadastralEnum.BAIXADA
        else:
            raise ValueError(
                f"Invalid situacao cadastral -- {situacao_cadastral} --"
                "Expected values: 01, 02, 03, 04, 08"
            )

    def get_tipo_pessoa(
        self, 
        atividade_economica_code: str
    ) -> TipoPessoaEnum:
        """
        SE NO CAMPO DO CARTÃO CNPJ "CÓDIGO E DESCRIÇÃO DA ATIVIDADE ECONÔMICA 
        PRINCIPAL" CONTIVER A PALAVRA COMERCIO OU INDUSTRIA VAMOS PREENCHER O 
        CAMPO TIPO PESSOA COM O VALOR CI - COMERCIO/INDUSTRIA SENÃO SEMPRE 
        OS - PRESTAÇÃO DE SERVIÇO.
        """
        if not self._atividade_economica_description:
            self._atividade_economica_description = self._get_atividade_economica_description(atividade_economica_code)

        normalized_atividade_economica_description = normalize_str(
            self._atividade_economica_description
        )

        if (
            "COMERCIO" in normalized_atividade_economica_description or 
            "INDUSTRIA" in normalized_atividade_economica_description
        ):
            return TipoPessoaEnum.CI
        else:
            return TipoPessoaEnum.OS 

    def get_cooperativa(self, razao_social: str) -> bool:
        normalized_razao_social = normalize_str(razao_social)

        if (
            "COOPERATIVA" in normalized_razao_social or
            "COOP" in normalized_razao_social
        ):
            return True
        
        return False
        
    def get_codigo_retencao(self, cooperativa: bool) -> str:
        """
       - CAMPO CÓDIGO DE RETENÇÃO: 
        * se cooperativa, codigo é 3280
        * se nao cooperativa, codigo é 1708
        """
        if cooperativa:
            return "3280"
        else:
            return "1708"
        
            
    def build(self, cnpj: CNPJ) -> Fornecedor:
        api_company = self.get_receita_api_company(cnpj)

        cooperativa = self.get_cooperativa(api_company.NOME_EMPRESARIAL)

        return Fornecedor.create(
            endereco=Endereco.create(
                endereco=api_company.END_LOGRADOURO or "",
                numero=api_company.END_NUMERO or "",
                bairro=api_company.END_BAIRRO or "",
                complemento=api_company.END_COMPLEMENTO or "",
                cep=CEP.create(cep=api_company.END_CEP) if api_company.END_CEP else None,
                municipio=self.get_municipio(api_company.END_MUNICIPIO) if api_company.END_MUNICIPIO else None,
                uf=api_company.END_UF or None,
            ),
            identificacao=FornecedorIdentificacao.create(
                cnpj=cnpj.value,
                razao_social=api_company.NOME_EMPRESARIAL or "",
                nome_fantasia=api_company.NOME_FANTASIA or None,
            ),
            dados_cadastrais=FornecedorDadosCadastrais.create(
                porte=self.get_porte(api_company.PORTE),
                opt_simples_nacional=self.get_opt_simples_nacional(cnpj),
                situacao_cadastral=self.get_situacao_cadastral(api_company.SIT_CADASTRAL),
                tipo_pessoa=self.get_tipo_pessoa(api_company.CNAE_PRINCIPAL_COD),
                vinculo_sebrae=VinculoSebraeEnum.Z, # sem vinculo sempre
                federacao=FederacaoEnum.NAO, # nao federacao sempre
                cooperativa=cooperativa,
                codigo_retencao=self.get_codigo_retencao(cooperativa),
            ),
            dados_contato=FornecedorDadosContato.create(
                ddd=DDD.from_value(api_company.DDD1) if api_company.DDD1 else None,
            ),
        )

