import json
import uuid
import time
from typing import Any

import pika


RABBIT_USER = "super.mei"
RABBIT_PASSWORD = "Sebrae01"
RABBIT_HOST = "10.3.18.1"
RABBIT_PORT = 5672

QUEUE_NAME = "cnpj.rpc"


class CartaoCNPJQueueRequester:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
    ) -> None:
        credentials = pika.PlainCredentials(username, password)

        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials,
            virtual_host="quebracapctha",
            client_properties={
                "connection_name": "super_mei",
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

    def call(
        self,
        queue: str,
        body: dict[str, Any],
        timeout: int = 600,
    ) -> dict[str, Any]:
        self.response = None
        self.correlation_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange="",
            routing_key=queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.correlation_id,
                content_type="application/json",
            ),
            body=json.dumps(body),
        )

        start_time = time.time()

        while self.response is None:
            self.connection.process_data_events(time_limit=1)

            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                raise TimeoutError(
                    f"RPC call to queue '{queue}' timed out after {timeout} seconds."
                )

        return self.response

    def close(self) -> None:
        if self.connection and self.connection.is_open:
            self.connection.close()


def consult_cnpj(cnpj: str) -> dict[str, Any]:
    client = RabbitMQRPCClient(
        host=RABBIT_HOST,
        port=RABBIT_PORT,
        username=RABBIT_USER,
        password=RABBIT_PASSWORD,
    )

    try:
        response = client.call(
            queue=QUEUE_NAME,
            body={
                "action": "cnpj.consultation",
                "cnpj": cnpj,
            },
            timeout=600,
        )

        return response

    finally:
        client.close()


if __name__ == "__main__":
    cnpj = "07526557000130"
    print(RABBIT_USER, RABBIT_PASSWORD, RABBIT_HOST, RABBIT_PORT)
    try:
        response = consult_cnpj(cnpj)
        print(json.dumps(response, indent=4, ensure_ascii=False))

    except TimeoutError as error:
        print(f"Timeout error: {error}")

    except pika.exceptions.AMQPConnectionError as error:
        print(f"RabbitMQ connection error: {error}")

    except Exception as error:
        print(f"Unexpected error: {error}")