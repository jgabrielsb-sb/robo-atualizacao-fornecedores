from app.domain.entities.fornecedor.fornecedor_entity import Fornecedor
from app.domain.enums import PorteEnum, SituacaoCadastralEnum, TipoPessoaEnum
from app.infra.api_requester.protheus_api_requester.models import (
    ClassificacaoProtheus,
    FederacaoProtheus,
    FornecedorUpdateOnProtheus,
    SimNaoProtheus,
    SimplesNacionalProtheus,
    TipoFornecedorProtheus,
    TipoPessoaProtheus,
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

    _SITUACAO_TO_MOTI_BLQ: dict[
        SituacaoCadastralEnum,
        str,
    ] = {
        SituacaoCadastralEnum.ATIVA: "",
        SituacaoCadastralEnum.INAPTA: "000009", #"000009 EMPRESA INAPTA", 
        SituacaoCadastralEnum.SUSPENSA: "000011", #"000011 EMPRESA SUSPENSA",
        SituacaoCadastralEnum.BAIXADA: "000010", #"000010 EMPRESA BAIXADA",
    }

    _TIPO_PESSOA_TO_CTIP_PESSOA : dict[
        TipoPessoaEnum,
        TipoPessoaProtheus,
    ] = {
        TipoPessoaEnum.CI: TipoPessoaProtheus.CI,
        TipoPessoaEnum.PF: TipoPessoaProtheus.PF,
        TipoPessoaEnum.OS: TipoPessoaProtheus.OS,
    }

    def build(self, fornecedor: Fornecedor) -> FornecedorUpdateOnProtheus:
        dc     = fornecedor.dados_cadastrais
        ident  = fornecedor.identificacao
        end    = fornecedor.endereco
        contato = fornecedor.dados_contato

        for_ativ = self._SITUACAO_TO_FOR_ATIV[dc.situacao_cadastral]
        moti_blq = self._SITUACAO_TO_MOTI_BLQ[dc.situacao_cadastral]
        
        return FornecedorUpdateOnProtheus(
            CNPJ_For=ident.cnpj.value,
            Nome_For=ident.razao_social[:50],
            Nome_Red=ident.nome_fantasia or "",
            Ende_For=end.endereco or "",
            Nume_End=end.numero or "",
            Cmpl_End=end.complemento or "",
            Bair_For=end.bairro or "",
            Esta_For=end.uf or "",
            Codi_Mun=end.municipio.codigo_ibge.value if end.municipio else "",
            Muni_For=end.municipio.nome if end.municipio else "",
            CEP_Forn=end.cep.value if end.cep else "",
            DDD_Forn=contato.ddd.value if contato.ddd else "",
            Tipo_Forn=TipoFornecedorProtheus.PESSOA_JURIDICA,
            Classifi=self._PORTE_TO_CLASSIFI[dc.porte],
            For_Ativ=for_ativ,
            Moti_Blq=self._SITUACAO_TO_MOTI_BLQ[dc.situacao_cadastral],
            Simples=SimplesNacionalProtheus.SIM if dc.opt_simples_nacional else SimplesNacionalProtheus.NAO,
            Cod_Rete=dc.codigo_retencao,
            Vinc_Seb=VinculoSebraeProtheus.SEM_VINCULO,
            Federaca=FederacaoProtheus.NAO,
            Cooperat=SimNaoProtheus.SIM if dc.cooperativa else SimNaoProtheus.NAO,
            cTipPess=self._TIPO_PESSOA_TO_CTIP_PESSOA[dc.tipo_pessoa],
        )
