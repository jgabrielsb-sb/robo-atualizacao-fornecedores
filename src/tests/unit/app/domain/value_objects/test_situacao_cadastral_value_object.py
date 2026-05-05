from app.domain.value_objects import SituacaoCadastral

import pytest

def test_should_create_situacao_cadastral_with_empty_motivo_bloqueio():
    situacao_cadastral = SituacaoCadastral.create(
        ativo=True,
        bloqueado=False,
        motivo_bloqueio=None,
    )
    assert situacao_cadastral.ativo == True
    assert situacao_cadastral.bloqueado == False
    assert situacao_cadastral.motivo_bloqueio is None

def test_should_create_situacao_cadastral_with_motivo_bloqueio():
    situacao_cadastral = SituacaoCadastral.create(
        ativo=True,
        bloqueado=True,
        motivo_bloqueio='Motivo de bloqueio',
    )
    assert situacao_cadastral.ativo == True
    assert situacao_cadastral.bloqueado == True
    assert situacao_cadastral.motivo_bloqueio == 'Motivo de bloqueio'

def test_should_raise_error_when_types_are_wrong():
    # ativo is not a boolean
    with pytest.raises(TypeError) as e:
        SituacaoCadastral.create(
            ativo='True',
            bloqueado=False,
            motivo_bloqueio=None,
        )
    assert "ativo" in str(e.value)

    # bloqueado is not a boolean
    with pytest.raises(TypeError) as e:
        SituacaoCadastral.create(
            ativo=True,
            bloqueado='True',
            motivo_bloqueio=None,
        )
    assert "bloqueado" in str(e.value)

    # motivo_bloqueio is not a string
    with pytest.raises(TypeError) as e:
        SituacaoCadastral.create(
            ativo=True,
            bloqueado=True,
            motivo_bloqueio=123,
        )
    assert "motivo_bloqueio" in str(e.value)