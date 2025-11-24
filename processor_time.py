"""
Time Tracker Processor - Container Service
"""

from rabbitmq_bus import RabbitMQEventBus
from event_processors import TimeTracker
import time
import signal
import sys


def signal_handler(sig, frame):
    print('\n🛑 Encerrando Time Tracker...')
    sys.exit(0)


def main():
    print("=" * 70)
    print("⏱️  TIME TRACKER PROCESSOR")
    print("=" * 70)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🔌 Conectando ao RabbitMQ...")
    event_bus = RabbitMQEventBus(host='rabbitmq', port=5672)

    processor = TimeTracker()

    print("📝 Registrando subscribers...")
    event_bus.subscribe("game_start", processor.on_game_start)
    event_bus.subscribe("game_pause", processor.on_game_pause)
    event_bus.subscribe("game_resume", processor.on_game_resume)

    print("✅ Time Tracker pronto!")
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
