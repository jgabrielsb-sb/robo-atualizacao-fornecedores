from typing import Any, Optional
from pydantic import BaseModel
import json
import pika
import uuid
import time

from app.domain.value_objects import CNPJ
from app.infra.queue.exceptions import QueueConnectionError

class QueueConfig(BaseModel):
    host: str
    port: str
    virtual_host: str
    username: str
    password: str
    connection_name: str
    queue_name: str


class RPCCartaoCNPJQueueRequester:
    def __init__(
        self,
        config: QueueConfig,
        timeout: int = 300
    ):
        self._config = config
        self._timeout = timeout
        self._response = None
        self._correlation_id = str(uuid.uuid4())
        self._connection = self._get_connection(self._config)
        self._channel = self._get_channel(self._connection)
        self._callback_queue = self._get_callback_queue_to_receive_response(self._channel)

    def _get_connection(self, config: QueueConfig):
        try:
            plain_credentials = pika.PlainCredentials(
                config.username, config.password
            )

            parameters = pika.ConnectionParameters(
                host=config.host,
                port=config.port,
                credentials=plain_credentials,
                virtual_host=config.virtual_host,
                client_properties={
                    "connection_name": config.connection_name
                }
            )

            return pika.BlockingConnection(parameters)
        except Exception as e:
            raise QueueConnectionError(
                f"Error while connection to queue: {e}"
            ) from e

    def _get_channel(self, connection: pika.BlockingConnection) :
        channel = connection.channel()
        return channel

    def _on_response(self, ch, method, props, body: bytes):
        if props.correlation_id == self._correlation_id:
            self._response = json.loads(body.decode("utf-8"))

    def _get_callback_queue_to_receive_response(self, channel):
        result = channel.queue_declare(queue="", exclusive=True)
        return result.method.queue
    
    def _wait_for_response(self):
        start_time = time.time()
        while self._response is None:
            self._connection.process_data_events(time_limit=1)
            elapsed_time = time.time() - start_time
            if elapsed_time > self._timeout:
                raise TimeoutError("Timeout waiting for response")
        
        return self._response

    def get_response(self, cnpj: CNPJ):
        self._channel.basic_consume(
            queue=self._callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True,
        )

        self._channel.basic_publish(
            exchange="",
            routing_key=self._config.queue_name,
            body=json.dumps({
                "action": "cnpj.consultation",
                "cnpj": cnpj.value,
            }).encode("utf-8"),
            properties=pika.BasicProperties(
                reply_to=self._callback_queue,
                correlation_id=self._correlation_id,
            ),
        )

        response = self._wait_for_response()
        return response



