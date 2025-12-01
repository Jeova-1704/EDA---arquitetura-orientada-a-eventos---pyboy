import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rabbitmq_bus import RabbitMQEventBus


class BattleProcessor:


    def __init__(self):
        self.battle_count = 0
        self.battles = []

    def on_battle_start(self, data):

        self.battle_count += 1
        self.battles.append({
            "battle_number": self.battle_count,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
        print(f"⚔️  [BATTLE PROCESSOR] Batalha #{self.battle_count} iniciada! "
              f"Posição: {data.get('position')}, Mapa: {data.get('map_id')}")


def main():

    print("=" * 70)
    print("⚔️  BATTLE PROCESSOR SERVICE")
    print("=" * 70)

    
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))

    
    print(f"🔌 Conectando ao RabbitMQ em {rabbitmq_host}:{rabbitmq_port}...")
    try:
        event_bus = RabbitMQEventBus(host=rabbitmq_host, port=rabbitmq_port)
        print("✅ Conectado ao RabbitMQ!")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return

    
    processor = BattleProcessor()

    
    print("📡 Registrando subscriber para 'battle_start'...")
    event_bus.subscribe("battle_start", processor.on_battle_start)
    print("✅ Subscriber registrado!")

    print("\n⚔️  [BATTLE PROCESSOR] Pronto! Aguardando eventos de batalha...")
    print("💡 Pressione Ctrl+C para encerrar\n")

    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando Battle Processor...")
        event_bus.close()
        print(f"📊 Total de batalhas processadas: {processor.battle_count}")
        print("✅ Serviço encerrado!")


if __name__ == "__main__":
    main()
