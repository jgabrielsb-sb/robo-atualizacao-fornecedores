from app.domain.entities.fornecedor.fornecedor_entity import Fornecedor
from app.domain.enums import PorteEnum, SituacaoCadastralEnum
from app.infra.api_requester.protheus_api_requester.models import (
    ClassificacaoProtheus,
    FederacaoProtheus,
    FornecedorUpdateOnProtheus,
    SimNaoProtheus,
    SimplesNacionalProtheus,
    TipoFornecedorProtheus,
    VinculoSebraeProtheus,
)


class FornecedorToProtheusBuilder:
    _PORTE_TO_CLASSIFI: dict[PorteEnum, ClassificacaoProtheus] = {
        PorteEnum.EIRELI: ClassificacaoProtheus.EIRELI,
        PorteEnum.EP:     ClassificacaoProtheus.EMPRESA_PUBLICA,
        PorteEnum.EPP:    ClassificacaoProtheus.EMPRESA_PEQUENO_PORTE,
        PorteEnum.ME:     ClassificacaoProtheus.MICRO_EMPRESA,
        PorteEnum.MEI:    ClassificacaoProtheus.MEI,
        PorteEnum.N:      ClassificacaoProtheus.NORMAL,
        PorteEnum.PF:     ClassificacaoProtheus.PESSOA_FISICA,
        PorteEnum.SFL:    ClassificacaoProtheus.SEM_FINS_LUCRATIVOS,
        PorteEnum.D:      ClassificacaoProtheus.DEMAIS,
    }

    _SITUACAO_TO_FOR_ATIV: dict[
        SituacaoCadastralEnum,
        SimNaoProtheus,
    ] = {
        SituacaoCadastralEnum.ATIVA: SimNaoProtheus.SIM,
        SituacaoCadastralEnum.INAPTA: SimNaoProtheus.NAO,
        SituacaoCadastralEnum.SUSPENSA: SimNaoProtheus.NAO,
        SituacaoCadastralEnum.BAIXADA: SimNaoProtheus.NAO,
    }

    def build(self, fornecedor: Fornecedor) -> FornecedorUpdateOnProtheus:
        dc     = fornecedor.dados_cadastrais
        ident  = fornecedor.identificacao
        end    = fornecedor.endereco
        contato = fornecedor.dados_contato

        for_ativ = self._SITUACAO_TO_FOR_ATIV[dc.situacao_cadastral]

        return FornecedorUpdateOnProtheus(
            CNPJ_For=ident.cnpj.value,
            Nome_For=ident.razao_social,
            Nome_Red=ident.nome_fantasia,
            Ende_For=end.endereco,
            Nume_End=end.numero,
            Cmpl_End=end.complemento,
            Bair_For=end.bairro,
            Esta_For=end.uf,
            Codi_Mun=end.municipio.codigo_ibge.value,
            Muni_For=end.municipio.nome,
            CEP_Forn=end.cep.value,
            DDD_Forn=contato.ddd.value,
            Tipo_Forn=TipoFornecedorProtheus.PESSOA_JURIDICA,
            Classifi=self._PORTE_TO_CLASSIFI[dc.porte],
            For_Ativ=for_ativ,
            Simples=SimplesNacionalProtheus.SIM if dc.opt_simples_nacional else SimplesNacionalProtheus.NAO,
            Cod_Rete=dc.codigo_retencao,
            Vinc_Seb=VinculoSebraeProtheus.SEM_VINCULO,
            Federaca=FederacaoProtheus.NAO,
            Cooperat=SimNaoProtheus.SIM if dc.cooperativa else SimNaoProtheus.NAO,
        )
