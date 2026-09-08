"""
Runs the production get-and-update-fornecedores workflow for a single
fornecedor, bypassing the real "get fornecedores to update" step with a
fixed CNPJ so this fornecedor can be updated in isolation.

Fornecedor: Prevesat Solução Em Engenharia Ltda
CNPJ: 21.966.327/0001-92

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

MOCK_FORNECEDOR = Fornecedor(id=UUID('e3a2de99-88e6-42b3-a2d6-10bbf22a14a5'), endereco=Endereco(endereco='R ENGENHEIRO ALVES DE SOUZA', numero='245', bairro='CENTRO', cep=CEP(value='48602080', formatted=''), municipio=Municipio(nome='PAULO AFONSO', codigo_ibge=CodigoMunicipioIBGE(value='24009')), complemento='SALA A', uf='BAHIA'), identificacao=FornecedorIdentificacao(cnpj=CNPJ(value='21966327000192', formatted='21.966.327/0001-92'), razao_social='CONSESMT ENGENHARIA LTDA', nome_fantasia='CONSESMT ENGENHARIA'), dados_cadastrais=FornecedorDadosCadastrais(opt_simples_nacional=True, vinculo_sebrae=VinculoSebraeEnum.Z, federacao=FederacaoEnum.NAO, cooperativa=False, codigo_retencao='1708', situacao_cadastral=SituacaoCadastralEnum.ATIVA, tipo_pessoa=TipoPessoaEnum.OS, tipo_contrato_social=None, porte=None), dados_contato=FornecedorDadosContato(ddd=DDD(value='75')))


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
        "Finished run_update_21966327000192",
        extra={"result": result.model_dump()},
    )
