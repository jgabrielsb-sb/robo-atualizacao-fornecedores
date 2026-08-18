"""
Runs the production get-and-update-fornecedores workflow for a single
fornecedor, bypassing the real "get fornecedores to update" step with a
fixed CNPJ so this fornecedor can be updated in isolation.

Fornecedor: IEL
CNPJ: 12.157.863/0001-56

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

MOCK_FORNECEDOR = Fornecedor(id=UUID('39a6df56-926e-4d40-bbd9-894b62f718b6'), endereco=Endereco(endereco='FERNANDES LIMA', numero='385', bairro='FAROL', cep=CEP(value='57055000', formatted=''), municipio=Municipio(nome='MACEIO', codigo_ibge=CodigoMunicipioIBGE(value='04302')), complemento=None, uf=None), identificacao=FornecedorIdentificacao(cnpj=CNPJ(value='12157863000156', formatted='12.157.863/0001-56'), razao_social='INSTITUTO EUVALDO LODI NUCLEO REGIONAL DE ALAGOAS', nome_fantasia='IEL/AL'), dados_cadastrais=FornecedorDadosCadastrais(opt_simples_nacional=False, vinculo_sebrae=VinculoSebraeEnum.Z, federacao=FederacaoEnum.NAO, cooperativa=False, codigo_retencao='1708', situacao_cadastral=SituacaoCadastralEnum.ATIVA, tipo_pessoa=TipoPessoaEnum.CI, tipo_contrato_social=None, porte=None), dados_contato=FornecedorDadosContato(ddd=DDD(value='82')))


class SingleFornecedorMock(GetFornecedoresToUpdatePort):
    def get(self) -> list[Fornecedor]:
        return [MOCK_FORNECEDOR]


def build_workflow() -> GetAndUpdateFornecedoresWorkflow:
    container = Container()
    return GetAndUpdateFornecedoresWorkflow(
        get_fornecedores_to_update=SingleFornecedorMock(),
        build_fornecedor=container.adapter_provider.get_build_fornecedor_via_receita_api_adapter(),
        update_fornecedor=container.adapter_provider.get_update_fornecedor_via_protheus_api_adapter(),
    )


if __name__ == "__main__":
    workflow = build_workflow()
    result = workflow.run()
    logger.info(
        "Finished run_update_12157863000156",
        extra={"result": result.model_dump()},
    )
