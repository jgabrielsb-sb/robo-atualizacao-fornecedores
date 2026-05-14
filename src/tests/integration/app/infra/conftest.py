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

@pytest.fixture
def fornecedor_to_update_with_cpf_data() -> dict:
    """Fornecedor whose CPF_CNPJ is a raw CPF (11 digits, no formatting)."""
    return {
        "LOJA": "01",
        "CODIGO": "000013",
        "NOME": "RESMA COMERCIAL DIST. DE PAPEIS LTDA",
        "NOME_FANTASIA": "RESMA COMERCIAL DIST",
        "CPF_CNPJ": "08325475498",
    }


@pytest.fixture
def fornecedor_to_update_with_cnpj_data() -> dict:
    """Fornecedor whose CPF_CNPJ is a raw CNPJ (14 digits, no formatting)."""
    return {
        "LOJA": "01",
        "CODIGO": "000013",
        "NOME": "RESMA COMERCIAL DIST. DE PAPEIS LTDA",
        "NOME_FANTASIA": "RESMA COMERCIAL DIST",
        "CPF_CNPJ": "08626186000109",
    }
