"""
Step Counter Processor - Container Service
Roda como serviço independente consumindo do RabbitMQ.
"""

from rabbitmq_bus import RabbitMQEventBus
from event_processors import StepCounter
import time
import signal
import sys


def signal_handler(sig, frame):
    """Handler para Ctrl+C"""
    print('\n🛑 Encerrando Step Counter...')
    sys.exit(0)


def main():
    print("=" * 70)
    print("👣 STEP COUNTER PROCESSOR")
    print("=" * 70)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🔌 Conectando ao RabbitMQ...")
    event_bus = RabbitMQEventBus(host='rabbitmq', port=5672)

    processor = StepCounter()

    print("📝 Registrando subscriber para 'step'...")
    event_bus.subscribe("step", processor.on_step)

    print("✅ Step Counter pronto!")
    print("🎧 Aguardando eventos...\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n🛑 Encerrando...')
    finally:
        event_bus.close()


if __name__ == "__main__":
    main()
