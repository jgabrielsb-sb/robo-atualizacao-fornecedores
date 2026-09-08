"""
Runs the production get-and-update-fornecedores workflow for a single
fornecedor, bypassing the real "get fornecedores to update" step with a
fixed CNPJ so this fornecedor can be updated in isolation.

Fornecedor: Frln Advogados
CNPJ: 26.705.113/0001-86

MOCK_FORNECEDOR below is the fornecedor's CURRENT (pre-update) state, fetched via
FornecedoresAPIRequester.get_fornecedor_to_update_by_cpf_cnpj() -- i.e. the real
"/v1/fornecedores-to-update/cpf-cnpj/{cpf_cnpj}" route -- when this script was
generated. It stands in for the real "get fornecedores to update" step, which
normally returns every fornecedor pending an update; here it is scoped to just
this one CNPJ.

GetAndUpdateFornecedoresWorkflow.build_fornecedor() logs this "before" state as
`input` alongside the freshly rebuilt (Receita-sourced) "after" state as `output`,
so running this script produces a before/after comparison for this fornecedor.
"""
import logging
from uuid import UUID

import app.logging.logger
from app.composition.container import Container
from app.domain import (
    CEP,
    DDD,
    CNPJ,
    Municipio,
    CodigoMunicipioIBGE,
    Endereco,
    Fornecedor,
    FornecedorIdentificacao,
    FornecedorDadosCadastrais,
    FornecedorDadosContato,
    SituacaoCadastralEnum,
    VinculoSebraeEnum,
    FederacaoEnum,
    TipoPessoaEnum,
    PorteEnum,
)
from app.domain.enums import TipoContratoSocialEnum
from app.application.ports import GetFornecedoresToUpdatePort
from app.application.use_cases.workflows import GetAndUpdateFornecedoresWorkflow

logger = logging.getLogger(__name__)

MOCK_FORNECEDOR = Fornecedor(id=UUID('e9534d52-9c02-40b8-b585-51d6db5a989c'), endereco=Endereco(endereco='DA PAZ', numero='1864', bairro='CENTRO', cep=CEP(value='57020440', formatted=''), municipio=Municipio(nome='MACEIO', codigo_ibge=CodigoMunicipioIBGE(value='04302')), complemento='SALA  1003 TERRA BRASILIS', uf='ALAGOAS'), identificacao=FornecedorIdentificacao(cnpj=CNPJ(value='26705113000186', formatted='26.705.113/0001-86'), razao_social='FIREMAN RABELO LAMENHA E NOBRE SOC ADVOG', nome_fantasia='FRLN ADVOGADOS'), dados_cadastrais=FornecedorDadosCadastrais(opt_simples_nacional=True, vinculo_sebrae=VinculoSebraeEnum.Z, federacao=FederacaoEnum.NAO, cooperativa=False, codigo_retencao='1708', situacao_cadastral=SituacaoCadastralEnum.ATIVA, tipo_pessoa=TipoPessoaEnum.OS, tipo_contrato_social=None, porte=None), dados_contato=FornecedorDadosContato(ddd=DDD(value='82')))


class SingleFornecedorMock(GetFornecedoresToUpdatePort):
    def get(self) -> list[Fornecedor]:
        return [MOCK_FORNECEDOR]


def build_workflow() -> GetAndUpdateFornecedoresWorkflow:
    container = Container()
    return GetAndUpdateFornecedoresWorkflow(
        get_fornecedores_to_update=SingleFornecedorMock(),
        build_fornecedor=container.adapter_provider.get_build_fornecedor_via_receita_api_adapter(),
        update_fornecedor=container.adapter_provider.get_update_fornecedor_via_protheus_api_adapter(),
        persist_updated_fornecedor=container.adapter_provider.get_persist_updated_fornecedor_via_fornecedores_api_adapter(),
    )


if __name__ == "__main__":
    workflow = build_workflow()
    result = workflow.run()
    logger.info(
        "Finished run_update_26705113000186",
        extra={"result": result.model_dump()},
    )
