from typing import Any

import json
import pika

from app.application.ports.fornecedor.send_updated_fornecedor_to_ppe_port import (
    SendUpdatedFornecedorToPPEPort,
)
from app.application.ports.fornecedor.updated_fornecedor_repository_port import (
    PersistUpdatedFornecedorResult,
)
from app.domain.value_objects import CNPJ
from app.infra.queue.rpc_queue_requester import QueueConfig


class SendUpdatedFornecedorToPPEViaQueueError(Exception):
    pass


class SendUpdatedFornecedorToPPEViaQueue(SendUpdatedFornecedorToPPEPort):
    def __init__(
        self,
        config: QueueConfig,
    ):
        self._config = config

    def send(self, atualizacao_fornecedor: PersistUpdatedFornecedorResult) -> Any:
        try:
            cnpj = CNPJ.create(cnpj=atualizacao_fornecedor.cnpj)

            plain_credentials = pika.PlainCredentials(
                self._config.username, self._config.password
            )
            parameters = pika.ConnectionParameters(
                host=self._config.host,
                port=self._config.port,
                credentials=plain_credentials,
                virtual_host=self._config.virtual_host,
                client_properties={
                    "connection_name": self._config.connection_name
                }
            )

            connection = pika.BlockingConnection(parameters)
            try:
                channel = connection.channel()
                channel.basic_publish(
                    exchange="",
                    routing_key=self._config.queue_name,
                    body=json.dumps({"cgc": cnpj.value}).encode("utf-8"),
                )
            finally:
                connection.close()
        except Exception as e:
            raise SendUpdatedFornecedorToPPEViaQueueError(
                f"Failed to send updated fornecedor {atualizacao_fornecedor.cnpj} to PPE via queue: {e}"
            ) from e
