"""
RabbitMQ Event Bus - Broker externo para arquitetura orientada a eventos.
Substitui o Event Bus local por RabbitMQ para comunicação entre processos.
"""

import pika
import json
import threading
from typing import Callable, Dict, Any
import time


class RabbitMQEventBus:
    """
    Event Bus usando RabbitMQ como broker externo.
    Mantém a mesma API do Event Bus local para compatibilidade.
    """

    def __init__(self, host='localhost', port=5672, exchange='pokemon_events', username='pokemon', password='pokemon123'):
        """
        Args:
            host: Hostname do RabbitMQ
            port: Porta do RabbitMQ
            exchange: Nome do exchange (topic exchange)
            username: Usuário do RabbitMQ
            password: Senha do RabbitMQ
        """
        self.host = host
        self.port = port
        self.exchange = exchange
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        self.callbacks = {}  # {event_type: [callbacks]}
        self.consumer_threads = {}

        # Conectar ao RabbitMQ
        self._connect()

    def _connect(self, max_retries=5, retry_delay=2):
        """Conecta ao RabbitMQ com retry."""
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

                # Declarar exchange do tipo topic
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
        """
        Publica um evento no RabbitMQ.

        Args:
            event_type: Tipo do evento (routing key)
            data: Dados do evento (será serializado como JSON)
        """
        try:
            # Serializar dados
            message = json.dumps(data if data is not None else {})

            # Publicar no exchange
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=event_type,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mensagem persistente
                    content_type='application/json'
                )
            )

        except Exception as e:
            print(f"❌ Erro ao publicar evento '{event_type}': {e}")

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """
        Registra um subscriber para um tipo de evento.

        Args:
            event_type: Tipo do evento
            callback: Função a ser chamada quando evento ocorrer
        """
        # Adicionar callback à lista
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)

        # Se é o primeiro subscriber deste tipo, criar fila e consumer
        if len(self.callbacks[event_type]) == 1:
            self._start_consumer(event_type)

    def _start_consumer(self, event_type: str):
        """
        Inicia um consumer thread para um tipo de evento.
        """
        def consume():
            try:
                # Criar nova conexão para esta thread
                credentials = pika.PlainCredentials(self.username, self.password)
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host,
                        port=self.port,
                        credentials=credentials
                    )
                )
                channel = connection.channel()

                # Declarar exchange
                channel.exchange_declare(
                    exchange=self.exchange,
                    exchange_type='topic',
                    durable=True
                )

                # Criar fila exclusiva para este tipo de evento
                queue_name = f"queue_{event_type}"
                channel.queue_declare(queue=queue_name, durable=True)

                # Bind fila ao exchange com routing key
                channel.queue_bind(
                    exchange=self.exchange,
                    queue=queue_name,
                    routing_key=event_type
                )

                # Callback que processa mensagens
                def on_message(ch, method, properties, body):
                    try:
                        # Deserializar dados
                        data = json.loads(body)

                        # Chamar todos os callbacks registrados
                        for callback in self.callbacks.get(event_type, []):
                            try:
                                callback(data)
                            except Exception as e:
                                print(f"❌ Erro em callback de '{event_type}': {e}")

                        # Confirmar processamento
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                    except Exception as e:
                        print(f"❌ Erro ao processar mensagem de '{event_type}': {e}")
                        ch.basic_nack(delivery_tag=method.delivery_tag)

                # Configurar consumer
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=on_message
                )

                print(f"🎧 Consumer iniciado para '{event_type}'")

                # Iniciar consumo (blocking)
                channel.start_consuming()

            except Exception as e:
                print(f"❌ Erro no consumer de '{event_type}': {e}")

        # Iniciar thread do consumer
        thread = threading.Thread(target=consume, daemon=True)
        thread.start()
        self.consumer_threads[event_type] = thread

        # Aguardar um pouco para thread iniciar
        time.sleep(0.2)

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """
        Remove um subscriber (compatibilidade com API local).

        Nota: Com RabbitMQ, subscribers rodam em threads separadas,
        então esta operação apenas remove o callback da lista.
        """
        if event_type in self.callbacks:
            try:
                self.callbacks[event_type].remove(callback)
            except ValueError:
                pass

    def clear(self) -> None:
        """Limpa todos os subscribers (compatibilidade com API local)."""
        self.callbacks.clear()

    def close(self):
        """Fecha a conexão com RabbitMQ."""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                print("🔌 Conexão com RabbitMQ fechada")
        except Exception as e:
            print(f"❌ Erro ao fechar conexão: {e}")

    def __del__(self):
        """Destrutor para garantir fechamento da conexão."""
        self.close()
