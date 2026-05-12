import pika
import json
import uuid
import time

from typing import Any, Dict
from pydantic import BaseModel

from app.application.ports import GetCartaoCNPJPort

class QueueConfig(BaseModel):
    host: str
    port: int
    virtual_host: str
    username: str
    password: str
    connection_name: str

class GetCartaoCNPJViaQueueRequester(GetCartaoCNPJPort):
    def __init__(
        self,
        config: QueueConfig,
    ) -> None:
        credentials = pika.PlainCredentials(config.username, config.password)

        parameters = pika.ConnectionParameters(
            host=config.host,
            port=config.port,
            credentials=credentials,
            virtual_host=config.virtual_host,
            client_properties={
                "connection_name": config.connection_name,
            }
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Creates a temporary exclusive queue to receive the response
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.response: dict[str, Any] | None = None
        self.correlation_id: str | None = None

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True,
        )

    def _on_response(self, ch, method, props, body: bytes) -> None:
        if props.correlation_id == self.correlation_id:
            self.response = json.loads(body.decode("utf-8"))

    def _get_response(self, cnpj: str) -> Dict[str, Any]:
        self.response = None
        self.correlation_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange="",
            routing_key="cnpj.rpc",
            body=json.dumps({
                "action": "cnpj.consultation",
                "cnpj": cnpj,
            }),
        )

        start_time = time.time()

        while self.response is None:
            self.connection.process_data_events(time_limit=1)

            elapsed_time = time.time() - start_time
            if elapsed_time > 600:
                raise TimeoutError("Timeout waiting for response")

        return self.response

    