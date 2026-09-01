from .fornecedor_repository_port import FornecedorRepositoryPort
from .update_fornecedor_port import UpdateFornecedorPort
from .updated_fornecedor_repository_port import (
    UpdatedFornecedorRepositoryPort,
    PersistUpdatedFornecedorResult,
)
from .get_updated_fornecedores_to_send_to_ppe_port import GetUpdatedFornecedoresToSendToPPEPort
from .send_updated_fornecedor_to_ppe_port import SendUpdatedFornecedorToPPEPort
from .send_updated_fornecedor_to_ppe_repository_port import SendUpdatedFornecedorToPPERepositoryPort
from .build_fornecedor import (
    BuildFornecedorPort,
    GetCartaoCNPJPort,
    GetOptSimplesNacionalPort,
    GetEnderecoPort,
)
