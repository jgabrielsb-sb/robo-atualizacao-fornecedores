"""
Shared fixtures for all integration tests under app/infra/.

Fixtures live here when they represent real external data shapes
that more than one test file needs — for example, the raw JSON
the Fornecedores API returns, which both the requester tests and
the adapter tests must mock at the HTTP boundary.

A fixture stays in its own test file until a second file needs it.
When that happens, it moves here.
"""
import pytest


# ---------------------------------------------------------------------------
# Fornecedores API — raw HTTP response shapes
#
# These dicts mirror the exact field names and value formats the real
# Fornecedores API returns. Both the requester integration tests and the
# adapter integration tests mock the same HTTP endpoint, so they share
# this data.
# ---------------------------------------------------------------------------

def _base_fornecedor_to_update_data() -> dict:
    """Fields common to every FornecedorToUpdate fixture, mirroring the real payload shape."""
    return {
        "LOJA": "01",
        "CODIGO": "000013",
        "NOME": "RESMA COMERCIAL DIST. DE PAPEIS LTDA",
        "NOME_FANTASIA": "RESMA COMERCIAL DIST",
        "TIPO_FORNEC": "JURIDICA",
        "ENDERECO": "AV FERNANDES LIMA",
        "NUMERO_END": "3349",
        "COMPLEM_END": "",
        "BAIRRO": "FAROL",
        "ESTADO": "ALAGOAS",
        "COD_MUNICIP": "04302",
        "MUNICIPIO": "MACEIO",
        "CEP_FORNEC": "57055000",
        "DDD_FONE": "82",
        "TELEFONE": "33364463",
        "E_MAIL": "",
        "INSCR_ESTAD": "24007177-8",
        "INSCR_MUNIC": "",
        "BLOQUEADO": "NÃO",
        "RELACAO_FOR": "Sem Vínculo",
        "MOTIVO_BLOQ": "",
        "INI_BLOQUEIO": "01/01/1900",
        "FIM_BLOQUEIO": "01/01/1900",
        "ATIVIDA_FOR": "Demais",
        "FOR_SIMPLES": "NÃO",
        "FEDERACAO": "NÃO",
        "COOPERATIVA": "NÃO",
        "TIPO_PESSOA": "Prestação de Serviço",
        "COD_RETENCAO": "1708",
    }


@pytest.fixture
def fornecedor_to_update_with_cpf_data() -> dict:
    """Fornecedor whose CPF_CNPJ is a raw CPF (11 digits, no formatting)."""
    return {
        **_base_fornecedor_to_update_data(),
        "CPF_CNPJ": "08325475498",
    }


@pytest.fixture
def fornecedor_to_update_with_cnpj_data() -> dict:
    """Fornecedor whose CPF_CNPJ is a raw CNPJ (14 digits, no formatting)."""
    return {
        **_base_fornecedor_to_update_data(),
        "CPF_CNPJ": "08626186000109",
    }

@pytest.fixture
def fornecedor_to_update_with_invalid_identifier_data() -> dict:
    return {
        **_base_fornecedor_to_update_data(),
        "CPF_CNPJ": "INVALID",
    }
