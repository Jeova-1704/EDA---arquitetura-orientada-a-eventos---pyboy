import pika
import json
import threading
from typing import Callable, Dict, Any
import time


class RabbitMQEventBus:

    def __init__(self, host='localhost', port=5672, exchange='pokemon_events', username='pokemon', password='pokemon123'):
        self.host = host
        self.port = port
        self.exchange = exchange
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        self.callbacks = {}
        self.consumer_threads = {}

        self._connect()

    def _connect(self, max_retries=5, retry_delay=2):
        for attempt in range(max_retries):
            try:
                print(f"🔌 Conectando ao RabbitMQ ({self.host}:{self.port})...")
                credentials = pika.PlainCredentials(self.username, self.password)
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host,
                        port=self.port,
                        credentials=credentials,
                        connection_attempts=3,
                        retry_delay=2
                    )
                )
                self.channel = self.connection.channel()

                self.channel.exchange_declare(
                    exchange=self.exchange,
                    exchange_type='topic',
                    durable=True
                )

                print(f"✅ Conectado ao RabbitMQ!")
                return

            except Exception as e:
                print(f"❌ Tentativa {attempt + 1}/{max_retries} falhou: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ Aguardando {retry_delay}s antes de tentar novamente...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(
                        f"Não foi possível conectar ao RabbitMQ após {max_retries} tentativas.\n"
                        f"Certifique-se de que o RabbitMQ está rodando: docker-compose up -d"
                    )

    def publish(self, event_type: str, data: Any = None) -> None:
        try:
            message = json.dumps(data if data is not None else {})

            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=event_type,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )

        except Exception as e:
            print(f"❌ Erro ao publicar evento '{event_type}': {e}")

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)

        if len(self.callbacks[event_type]) == 1:
            self._start_consumer(event_type)

    def _start_consumer(self, event_type: str):
        def consume():
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host,
                        port=self.port,
                        credentials=credentials
                    )
                )
                channel = connection.channel()

                channel.exchange_declare(
                    exchange=self.exchange,
                    exchange_type='topic',
                    durable=True
                )

                result = channel.queue_declare(
                    queue='',           
                    exclusive=True,     
                    auto_delete=True    
                )
                queue_name = result.method.queue  

                channel.queue_bind(
                    exchange=self.exchange,
                    queue=queue_name,
                    routing_key=event_type
                )

                def on_message(ch, method, properties, body):
                    try:
                        data = json.loads(body)

                        for callback in self.callbacks.get(event_type, []):
                            try:
                                callback(data)
                            except Exception as e:
                                print(f"❌ Erro em callback de '{event_type}': {e}")

                        ch.basic_ack(delivery_tag=method.delivery_tag)

                    except Exception as e:
                        print(f"❌ Erro ao processar mensagem de '{event_type}': {e}")
                        ch.basic_nack(delivery_tag=method.delivery_tag)

                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=on_message
                )

                print(f"🎧 Consumer iniciado para '{event_type}'")

                channel.start_consuming()

            except Exception as e:
                print(f"❌ Erro no consumer de '{event_type}': {e}")

        thread = threading.Thread(target=consume, daemon=True)
        thread.start()
        self.consumer_threads[event_type] = thread

        time.sleep(0.2)

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        if event_type in self.callbacks:
            try:
                self.callbacks[event_type].remove(callback)
            except ValueError:
                pass

    def clear(self) -> None:
        self.callbacks.clear()

    def close(self):
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                print("🔌 Conexão com RabbitMQ fechada")
        except Exception as e:
            print(f"❌ Erro ao fechar conexão: {e}")

    def __del__(self):
        self.close()
