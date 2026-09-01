import json
from datetime import datetime, timezone

import pytest
pytestmark = pytest.mark.unit

from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)
from app.infra.adapters.send_updated_fornecedor_to_ppe.send_updated_fornecedor_to_ppe_via_queue import (
    SendUpdatedFornecedorToPPEViaQueue,
    SendUpdatedFornecedorToPPEViaQueueError,
)
from app.infra.queue.rpc_queue_requester import QueueConfig

PIKA_BLOCKING_CONNECTION_PATH = (
    "app.infra.adapters.send_updated_fornecedor_to_ppe."
    "send_updated_fornecedor_to_ppe_via_queue.pika.BlockingConnection"
)


class FakeChannel:
    def __init__(self):
        self.published: list[dict] = []

    def basic_publish(self, exchange, routing_key, body):
        self.published.append({"exchange": exchange, "routing_key": routing_key, "body": body})


class FakeConnection:
    def __init__(self, channel: FakeChannel):
        self._channel = channel
        self.closed = False

    def channel(self) -> FakeChannel:
        return self._channel

    def close(self) -> None:
        self.closed = True


def make_config() -> QueueConfig:
    return QueueConfig(
        host="localhost",
        port="5672",
        virtual_host="/",
        username="user",
        password="password",
        connection_name="test",
        queue_name="ppe.company.update",
    )


def make_atualizacao_fornecedor(cnpj: str) -> PersistUpdatedFornecedorResult:
    now = datetime.now(timezone.utc)
    return PersistUpdatedFornecedorResult(
        id=1,
        cnpj=cnpj,
        step_update_on_ppe_attempt_count=0,
        step_update_on_ppe_status_id=1,
        created_at=now,
        updated_at=now,
    )


def test_should_send_cgc_message_with_only_digits(monkeypatch):
    fake_channel = FakeChannel()
    fake_connection = FakeConnection(fake_channel)
    monkeypatch.setattr(PIKA_BLOCKING_CONNECTION_PATH, lambda parameters: fake_connection)

    adapter = SendUpdatedFornecedorToPPEViaQueue(config=make_config())
    adapter.send(make_atualizacao_fornecedor("28738609000181"))

    assert len(fake_channel.published) == 1
    assert json.loads(fake_channel.published[0]["body"]) == {"cgc": "28738609000181"}


def test_should_strip_formatting_characters_from_cnpj(monkeypatch):
    fake_channel = FakeChannel()
    fake_connection = FakeConnection(fake_channel)
    monkeypatch.setattr(PIKA_BLOCKING_CONNECTION_PATH, lambda parameters: fake_connection)

    adapter = SendUpdatedFornecedorToPPEViaQueue(config=make_config())
    adapter.send(make_atualizacao_fornecedor("28.738.609/0001-81"))

    assert json.loads(fake_channel.published[0]["body"]) == {"cgc": "28738609000181"}


def test_should_close_the_connection_after_sending(monkeypatch):
    fake_channel = FakeChannel()
    fake_connection = FakeConnection(fake_channel)
    monkeypatch.setattr(PIKA_BLOCKING_CONNECTION_PATH, lambda parameters: fake_connection)

    adapter = SendUpdatedFornecedorToPPEViaQueue(config=make_config())
    adapter.send(make_atualizacao_fornecedor("28738609000181"))

    assert fake_connection.closed is True


def test_should_raise_adapter_error_when_connection_fails(monkeypatch):
    def _raise_connection_error(parameters):
        raise Exception("connection refused")

    monkeypatch.setattr(PIKA_BLOCKING_CONNECTION_PATH, _raise_connection_error)

    adapter = SendUpdatedFornecedorToPPEViaQueue(config=make_config())

    with pytest.raises(SendUpdatedFornecedorToPPEViaQueueError):
        adapter.send(make_atualizacao_fornecedor("28738609000181"))


def test_should_raise_adapter_error_when_cnpj_is_invalid(monkeypatch):
    def _fail_if_called(parameters):
        raise AssertionError("should not attempt to connect when the CNPJ is invalid")

    monkeypatch.setattr(PIKA_BLOCKING_CONNECTION_PATH, _fail_if_called)

    adapter = SendUpdatedFornecedorToPPEViaQueue(config=make_config())

    with pytest.raises(SendUpdatedFornecedorToPPEViaQueueError):
        adapter.send(make_atualizacao_fornecedor("123"))
