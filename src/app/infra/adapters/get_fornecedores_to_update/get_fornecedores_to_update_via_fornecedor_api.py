import logging

from app.application.ports import GetFornecedoresToUpdatePort, MunicipioLookupPort
from app.domain.entities import Fornecedor
from app.domain.entities.fornecedor import (
    FornecedorIdentificacao,
    FornecedorDadosCadastrais,
    FornecedorDadosContato,
)
from app.domain.enums import SituacaoCadastralEnum
from app.domain.value_objects import (
    CEP,
    CNPJ,
    CPF,
    Endereco,
    InvalidCNPJError,
    InvalidCPFError,
)
from app.infra.api_requester.fornecedores_api_requester import (
    FornecedoresAPIRequester,
    FornecedorToUpdate,
)

logger = logging.getLogger(__name__)


class GetFornecedoresToUpdateViaFornecedoresAPIError(Exception):
    pass


class GetFornecedoresToUpdateViaFornecedoresAPI(GetFornecedoresToUpdatePort):
    # Inverse of FornecedorToProtheusBuilder._SITUACAO_TO_MOTI_BLQ: the endpoint
    # only exposes Protheus's Moti_Blq code, not a SituacaoCadastral, so we map back.
    _MOTIVO_BLOQ_TO_SITUACAO_CADASTRAL: dict[str, SituacaoCadastralEnum] = {
        "": SituacaoCadastralEnum.ATIVA,
        "000009": SituacaoCadastralEnum.INAPTA,
        "000011": SituacaoCadastralEnum.SUSPENSA,
        "000010": SituacaoCadastralEnum.BAIXADA,
    }

    def __init__(
        self,
        fornecedores_api_requester: FornecedoresAPIRequester,
        municipio_lookup_port: MunicipioLookupPort,
    ):
        self._fornecedores_api_requester = fornecedores_api_requester
        self._municipio_lookup_port = municipio_lookup_port

    def _is_cpf(self, cpf_value: str) -> bool:
        try:
            CPF.create(cpf=cpf_value)
            return True
        except InvalidCPFError:
            return False

    def _get_situacao_cadastral(self, motivo_bloq: str) -> SituacaoCadastralEnum:
        normalized = motivo_bloq.strip()
        try:
            return self._MOTIVO_BLOQ_TO_SITUACAO_CADASTRAL[normalized]
        except KeyError:
            raise GetFornecedoresToUpdateViaFornecedoresAPIError(
                f"Cannot map MOTIVO_BLOQ to a SituacaoCadastral: {motivo_bloq!r}"
            )

    def _build_fornecedor(
        self,
        fornecedor_to_update: FornecedorToUpdate,
        cnpj: CNPJ,
    ) -> Fornecedor:
        municipio_name = fornecedor_to_update.MUNICIPIO.strip()
        return Fornecedor.create(
            endereco=Endereco.create(
                endereco=fornecedor_to_update.ENDERECO.strip() or None,
                numero=fornecedor_to_update.NUMERO_END.strip() or None,
                bairro=fornecedor_to_update.BAIRRO.strip() or None,
                complemento=fornecedor_to_update.COMPLEM_END.strip() or None,
                cep=CEP.create(cep=fornecedor_to_update.CEP_FORNEC) if fornecedor_to_update.CEP_FORNEC.strip() else None,
                municipio=self._municipio_lookup_port.get(municipio_name) if municipio_name else None,
                uf=fornecedor_to_update.ESTADO.strip() or None,
            ),
            identificacao=FornecedorIdentificacao.create(
                cnpj=cnpj.value,
                razao_social=fornecedor_to_update.NOME.strip(),
                nome_fantasia=fornecedor_to_update.NOME_FANTASIA.strip() or None,
            ),
            dados_cadastrais=FornecedorDadosCadastrais.create(
                porte=None,
                opt_simples_nacional=fornecedor_to_update.FOR_SIMPLES.strip().upper() == "SIM",
                situacao_cadastral=self._get_situacao_cadastral(fornecedor_to_update.MOTIVO_BLOQ),
                tipo_pessoa=fornecedor_to_update.TIPO_PESSOA.strip() or None,
                vinculo_sebrae=fornecedor_to_update.RELACAO_FOR,
                federacao=fornecedor_to_update.FEDERACAO,
                cooperativa=fornecedor_to_update.COOPERATIVA.strip().upper() == "SIM",
                codigo_retencao=fornecedor_to_update.COD_RETENCAO.strip(),
            ),
            dados_contato=FornecedorDadosContato.create(
                ddd=fornecedor_to_update.DDD_FONE.strip() or None,
            ),
        )

    def get(self) -> list[Fornecedor]:
        """
        Get the Fornecedores to update from the Fornecedores API Requester.
        Returns:
            list[Fornecedor]: The Fornecedores to update.
        """
        fornecedores = []
        fornecedores_to_update = self._fornecedores_api_requester.get_fornecedores_to_update() or []

        for fornecedor_to_update in fornecedores_to_update:
            if self._is_cpf(fornecedor_to_update.CPF_CNPJ):
                continue

            try:
                cnpj = CNPJ.create(cnpj=fornecedor_to_update.CPF_CNPJ)
            except InvalidCNPJError:
                continue

            try:
                fornecedores.append(self._build_fornecedor(fornecedor_to_update, cnpj))
            except Exception:
                logger.warning(
                    f"Failed to build fornecedor -- {cnpj.value} -- , skipping it",
                    exc_info=True,
                )

        return fornecedores
