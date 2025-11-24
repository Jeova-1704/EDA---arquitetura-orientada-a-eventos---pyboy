from rabbitmq_bus import RabbitMQEventBus
from event_processors import BattleCounter
import time
import signal
import sys


def signal_handler(sig, frame):
    print('\n🛑 Encerrando Battle Counter...')
    sys.exit(0)


def main():
    print("=" * 70)
    print("⚔️  BATTLE COUNTER PROCESSOR")
    print("=" * 70)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🔌 Conectando ao RabbitMQ...")
    event_bus = RabbitMQEventBus(host='rabbitmq', port=5672)

    processor = BattleCounter()

    print("📝 Registrando subscriber para 'battle_start'...")
    event_bus.subscribe("battle_start", processor.on_battle_start)

    print("✅ Battle Counter pronto!")
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
