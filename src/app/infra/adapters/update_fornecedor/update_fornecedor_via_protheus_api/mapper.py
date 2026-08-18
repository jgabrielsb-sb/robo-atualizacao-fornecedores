from typing import Optional

from app.domain.entities.fornecedor.fornecedor_entity import Fornecedor
from app.infra.api_requester.protheus_api_requester.models import FornecedorUpdateOnProtheus





class MapFornecedorToFornecedorToUpdate:
    def _get_ativo(self) -> bool:
        return True

    def _get_bloqueado(self) -> bool:
        return False

    def _get_motivo_bloqueio(self) -> Optional[str]:
        return None

    def map(
        self, 
        fornecedor: Fornecedor
    ) -> FornecedorUpdateOnProtheus:
        return FornecedorToUpdate.create(
            opt_simples_nacional=fornecedor.dados_cadastrais.opt_simples_nacional,
            razao_social=fornecedor.identificacao.razao_social,
            nome_fantasia=fornecedor.identificacao.nome_fantasia,
            porte=fornecedor.dados_cadastrais.porte,
            logradouro=fornecedor.endereco.endereco,
            numero=fornecedor.endereco.numero,
            bairro=fornecedor.endereco.bairro,
            municipio=fornecedor.endereco.municipio,
            ddd=fornecedor.dados_contato.ddd,
            ativo=self._get_ativo(),
            bloqueado=self._get_bloqueado(),
            motivo_bloqueio=self._get_motivo_bloqueio(),
            tipo_pessoa=fornecedor.dados_cadastrais.tipo_pessoa,
            vinculo_sebrae=fornecedor.dados_cadastrais.vinculo_sebrae,
            cooperativa=fornecedor.dados_cadastrais.cooperativa,
            codigo_retencao=fornecedor.dados_cadastrais.codigo_retencao,
            complemento=fornecedor.endereco.complemento,
        )

