from uuid import UUID

from app.composition.container import Container
from config.settings import settings
from app.domain import (
    CNPJ,
    CEP,
    DDD,
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

import logging
import app.logging.logger
import schedule
import time

from app.composition.container import Container
from config.settings import settings

container = Container()
use_case = container.get_get_and_update_fornecedores_workflow()
builder = container.adapter_provider.get_build_fornecedor_via_receita_api_adapter()

logger = logging.getLogger("main")

container = Container()
#adapter = container.adapter_provider.get_build_fornecedor_via_receita_api_adapter()
#get_fornecedores_to_update = container.adapter_provider.get_get_fornecedores_to_update_via_fornecedores_api_adapter()
"""
FORNECEDOR CNPJ 35739143000102
"""
BEFORE_FORNECEDOR2_A_DATA = Fornecedor(
    id=UUID('60ba8542-66bc-4a62-9d2a-4cb3234e91e5'),
    endereco=Endereco(
        endereco='RUA MATO GROSSO, 78 B',
        numero=None,
        bairro='JARAGUA',
        cep=CEP(value='57025090', formatted='57025-090'),
        municipio=Municipio(nome='MACEIO', codigo_ibge=CodigoMunicipioIBGE(value='2704302')),
        complemento=None,
        uf=None,
    ),
    identificacao=FornecedorIdentificacao(
        cnpj=CNPJ(value='35739143000102', formatted='35.739.143/0001-02'),
        razao_social='KD POST-DOOR SINALIZACAO LTDA.',
        nome_fantasia='KD POST-DOOR SINALIZ',
    ),
    dados_cadastrais=FornecedorDadosCadastrais(
        opt_simples_nacional=False,
        situacao_cadastral=SituacaoCadastralEnum.ATIVA,
        vinculo_sebrae=VinculoSebraeEnum.Z,
        federacao=FederacaoEnum.NAO,
        cooperativa=False,
        codigo_retencao='1708',
        tipo_pessoa=None,
        porte=None,
    ),
    dados_contato=FornecedorDadosContato(ddd=None),
)
## DEPOIS
AFTER_FORNECEDOR2_A_DATA = Fornecedor(
    id=UUID('60ba8542-66bc-4a62-9d2a-4cb3234e91e5'),
    endereco=Endereco(
        endereco='SA E ALBUQUERQUE',
        numero='780 E',
        bairro='JARAGUA',
        cep=CEP(value='57022180', formatted='57022-180'),
        municipio=Municipio(nome='MACEIO', codigo_ibge=CodigoMunicipioIBGE(value='2704302')),
        complemento='788',
        uf='AL',
    ),
    identificacao=FornecedorIdentificacao(
        cnpj=CNPJ(value='35739143000102', formatted='35.739.143/0001-02'),
        razao_social='AWD SINALIZACAO LTDA',
        nome_fantasia=None,
    ),
    dados_cadastrais=FornecedorDadosCadastrais(
        opt_simples_nacional=False,
        situacao_cadastral=SituacaoCadastralEnum.INAPTA,
        vinculo_sebrae=VinculoSebraeEnum.Z,
        federacao=FederacaoEnum.NAO,
        cooperativa=False,
        codigo_retencao='1708',
        tipo_pessoa=TipoPessoaEnum.OS,
        porte=PorteEnum.EPP,
    ),
    dados_contato=FornecedorDadosContato(ddd=None),
)

mock_fornecedores_to_update = None #[BEFORE_FORNECEDOR2_A_DATA, AFTER_FORNECEDOR2_A_DATA]
#workflow = container.get_get_and_update_fornecedores_workflow(mock_fornecedores_to_update=mock_fornecedores_to_update)

if __name__ == "__main__":
    #result = workflow.run()
    fornecedor = builder.build(CNPJ("09311176000139"))
    print('fornecedor built by builder: ', fornecedor)
