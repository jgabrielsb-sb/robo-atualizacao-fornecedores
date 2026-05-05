from dataclasses import dataclass
from uuid import UUID, uuid4

from app.domain.value_objects import Endereco
from .fornecedor_identificacao_entity import FornecedorIdentificacao
from .fornecedor_dados_cadastrais_entity import FornecedorDadosCadastrais
from .fornecedor_dados_contato_entity import FornecedorDadosContato

class InvalidFornecedorError(Exception):
    pass

@dataclass(frozen=True)
class Fornecedor:
    id: UUID
    endereco: Endereco
    identificacao: FornecedorIdentificacao
    dados_cadastrais: FornecedorDadosCadastrais
    dados_contato: FornecedorDadosContato

    def validate_types(self):
        if not isinstance(self.endereco, Endereco):
            raise TypeError("endereco must be a Endereco")
        if not isinstance(self.identificacao, FornecedorIdentificacao):
            raise TypeError("identificacao must be a FornecedorIdentificacao")
        if not isinstance(self.dados_cadastrais, FornecedorDadosCadastrais):
            raise TypeError("dados_cadastrais must be a FornecedorDadosCadastrais")
        if not isinstance(self.dados_contato, FornecedorDadosContato):
            raise TypeError("dados_contato must be a FornecedorDadosContato")
 
    def __post_init__(self):
        self.validate_types()
    
    @classmethod
    def create(
        cls,
        *,
        endereco: Endereco,
        identificacao: FornecedorIdentificacao,
        dados_cadastrais: FornecedorDadosCadastrais,
        dados_contato: FornecedorDadosContato,
    ) -> 'Fornecedor':
        return cls(
            id=uuid4(),
            endereco=endereco,
            identificacao=identificacao,
            dados_cadastrais=dados_cadastrais,
            dados_contato=dados_contato,
        )




