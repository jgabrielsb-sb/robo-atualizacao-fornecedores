from app.domain import (
    Fornecedor, 
    Endereco,
    CNPJ,
    FornecedorIdentificacao,
    FornecedorDadosCadastrais,
    FornecedorDadosContato,    
)

from app.application.ports import (
    GetOptSimplesNacionalPort, 
    GetCartaoCNPJPort, 
    GetEnderecoPort,
)

from app.domain.value_objects import CartaoCNPJ
from app.domain.enums import FederacaoEnum, TipoPessoaEnum, VinculoSebraeEnum

from dataclasses import fields, replace

from app.utils.normalize_str import normalize_str

class FornecedorBuilderServiceError(Exception):
    pass

class GetOptanteSimplesNacionalError(FornecedorBuilderServiceError):
    pass

class GetCartaoCNPJError(FornecedorBuilderServiceError):
    pass

class FornecedorBuilderService:
    def __init__(
        self,
        get_opt_simples_nacional_port: GetOptSimplesNacionalPort,
        get_cartao_cnpj_port: GetCartaoCNPJPort,
        get_endereco_port: GetEnderecoPort,
    ):
        self._get_opt_simples_nacional_port = get_opt_simples_nacional_port
        self._get_cartao_cnpj_port = get_cartao_cnpj_port
        self._get_endereco_port = get_endereco_port

    def _get_opt_simples_nacional(self, cnpj: CNPJ) -> bool:
        try:
            return self._get_opt_simples_nacional_port.get(cnpj)
        except Exception as e:
            raise GetOptanteSimplesNacionalError(f"Failed to get optante simples nacional: {e}") from e

    from dataclasses import fields, replace

    def _get_endereco(
        self,
        cnpj: CNPJ,
        cartao_cnpj: CartaoCNPJ,
    ) -> Endereco:
        """
        Builds the best possible Endereco.

        CartaoCNPJ is the primary source.
        If some address fields are missing, we fetch an alternative source
        and use it only to fill missing values.
        """
        cartao_cnpj_endereco = cartao_cnpj.endereco

        if cartao_cnpj_endereco is None:
            none_fields = [field.name for field in fields(Endereco)]
            cartao_cnpj_endereco = Endereco.create()
        else:
            none_fields = [
                field.name
                for field in fields(Endereco)
                if getattr(cartao_cnpj_endereco, field.name) is None
            ]

        if not none_fields:
            return cartao_cnpj_endereco

        alternative_endereco = self._get_endereco_port.get(cnpj=cnpj)

        if alternative_endereco is None:
            return cartao_cnpj_endereco

        values_to_replace = {}

        for field_name in none_fields:
            alternative_value = getattr(alternative_endereco, field_name)

            if alternative_value is not None:
                values_to_replace[field_name] = alternative_value

        if not values_to_replace:
            return cartao_cnpj_endereco

        return replace(
            cartao_cnpj_endereco,
            **values_to_replace,
        )

    def _get_cartao_cnpj(self, cnpj: CNPJ) -> CartaoCNPJ:
        try:
            return self._get_cartao_cnpj_port.get(cnpj)
        except Exception as e:
            raise GetCartaoCNPJError(f"Failed to get cartao cnpj: {e}") from e

    def _get_tipo_pessoa(self, atividade_economica_principal_str: str) -> TipoPessoaEnum:
        normalized_atividade_economica_principal_str = normalize_str(atividade_economica_principal_str)
        
        if (
            "COMERCIO" in normalized_atividade_economica_principal_str 
            or
            "INDUSTRIA" in normalized_atividade_economica_principal_str
        ):
            return TipoPessoaEnum.CI

        return TipoPessoaEnum.OS

    def _get_vinculo_sebrae(self) -> VinculoSebraeEnum:
        return VinculoSebraeEnum.Z 

    def _get_federacao(self) -> FederacaoEnum:
        return FederacaoEnum.NAO

    def _get_cooperativa(self, natureza_juridica: str) -> bool:
        return "COOPERATIVA" in normalize_str(natureza_juridica)

    def _get_codigo_retencao(self, cooperativa: bool) -> str:
        if cooperativa:
            return "3280"
        else:
            return "1708"

    def build(self, cnpj: CNPJ) -> Fornecedor:
        opt_simples_nacional = self._get_opt_simples_nacional(cnpj)
        cartao_cnpj = self._get_cartao_cnpj(cnpj)
        
        return Fornecedor.create(
            endereco=self._get_endereco(
                cnpj=cnpj,
                cartao_cnpj=cartao_cnpj,
            ),
            identificacao=FornecedorIdentificacao.create(
                cnpj=cnpj.value,
                razao_social=cartao_cnpj.razao_social,
                nome_fantasia=cartao_cnpj.nome_fantasia,
            ),
            dados_cadastrais=FornecedorDadosCadastrais.create(
                porte=cartao_cnpj.porte,
                opt_simples_nacional=opt_simples_nacional,
                situacao_cadastral=cartao_cnpj.situacao_cadastral,
                tipo_pessoa=self._get_tipo_pessoa(cartao_cnpj.atividade_economica_principal_str),
                vinculo_sebrae=self._get_vinculo_sebrae(),
                federacao=self._get_federacao(),
                cooperativa=self._get_cooperativa(cartao_cnpj.natureza_juridica),
                codigo_retencao=self._get_codigo_retencao(self._get_cooperativa(cartao_cnpj.natureza_juridica)),
            ),
            dados_contato=FornecedorDadosContato.create(
                ddd=cartao_cnpj.telefone.ddd,
            ),
        )
            

        