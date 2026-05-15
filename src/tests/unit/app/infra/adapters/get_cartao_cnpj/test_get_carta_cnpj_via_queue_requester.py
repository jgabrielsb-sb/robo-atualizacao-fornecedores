import pytest

from app.domain.value_objects import CNPJ, CartaoCNPJ
from app.infra.adapters.get_cartao_cnpj.get_cartao_cnpj_via_queue_requester import GetCartaoCNPJViaQueueRequester
from app.infra.adapters.exceptions import ErrorWhileGettingExternalDataError
from conftest import DATA


class FakeQueueRequester:
    def __init__(self, response: dict):
        self._response = response

    def get_response(self, cnpj: CNPJ) -> dict:
        return self._response


class FakeFailingQueueRequester:
    def get_response(self, cnpj: CNPJ) -> dict:
        raise Exception("queue connection failed")


@pytest.fixture
def make_adapter(fake_municipio_lookup_port):
    def _make(queue_response: dict) -> GetCartaoCNPJViaQueueRequester:
        return GetCartaoCNPJViaQueueRequester(
            queue_requester=FakeQueueRequester(queue_response),
            municipio_lookup_port=fake_municipio_lookup_port,
        )
    return _make


def test_should_raise_error_while_getting_external_data_when_queue_requester_raises(
    fake_municipio_lookup_port,
):
    adapter = GetCartaoCNPJViaQueueRequester(
        queue_requester=FakeFailingQueueRequester(),
        municipio_lookup_port=fake_municipio_lookup_port,
    )
    cnpj = CNPJ.create(cnpj="28738609000181")

    with pytest.raises(ErrorWhileGettingExternalDataError) as exc_info:
        adapter.get(cnpj)

    assert "error while getting the external data from the queue" in str(exc_info.value)


@pytest.mark.parametrize("data", DATA)
def test_should_return_correct_cartao_cnpj(data, make_adapter):
    adapter = make_adapter(data["queue_response"])
    cnpj = CNPJ.create(cnpj=data["queue_response"]["cnpj"])

    result = adapter.get(cnpj)

    assert isinstance(result, CartaoCNPJ)
    assert result == data["expected_result"]
