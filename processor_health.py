from rabbitmq_bus import RabbitMQEventBus
from event_processors import HealthTracker
import time
import signal
import sys


def signal_handler(sig, frame):
    print('\n🛑 Encerrando Health Tracker...')
    sys.exit(0)


def main():
    print("=" * 70)
    print("❤️  HEALTH TRACKER PROCESSOR")
    print("=" * 70)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🔌 Conectando ao RabbitMQ...")
    event_bus = RabbitMQEventBus(host='rabbitmq', port=5672)

    processor = HealthTracker()

    print("📝 Registrando subscriber para 'health_change'...")
    event_bus.subscribe("health_change", processor.on_health_change)

    print("✅ Health Tracker pronto!")
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
