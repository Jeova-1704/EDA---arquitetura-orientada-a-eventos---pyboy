import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rabbitmq_bus import RabbitMQEventBus


class PositionProcessor:

    def __init__(self):
        self.positions = []
        self.current_position = None
        self.current_map_id = None

    def on_position_change(self, data):
        self.current_position = data.get("position")
        self.current_map_id = data.get("map_id")

        self.positions.append({
            "timestamp": datetime.now().isoformat(),
            "position": self.current_position,
            "map_id": self.current_map_id
        })

        
        if len(self.positions) > 1:
            previous_map = self.positions[-2]["map_id"]
            if previous_map != self.current_map_id:
                print(f"📍 [POSITION PROCESSOR] Mudança de mapa! "
                      f"Mapa {previous_map} → Mapa {self.current_map_id}")


def main():
    print("=" * 70)
    print("📍 POSITION PROCESSOR SERVICE")
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

    
    processor = PositionProcessor()

    
    print("📡 Registrando subscriber para 'position_change'...")
    event_bus.subscribe("position_change", processor.on_position_change)
    print("✅ Subscriber registrado!")

    print("\n📍 [POSITION PROCESSOR] Pronto! Rastreando posição do jogador...")
    print("💡 Pressione Ctrl+C para encerrar\n")

    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando Position Processor...")
        event_bus.close()
        print(f"📊 Total de mudanças de posição: {len(processor.positions)}")
        if processor.current_position:
            print(f"📊 Posição final: {processor.current_position}, Mapa: {processor.current_map_id}")
        print("✅ Serviço encerrado!")


if __name__ == "__main__":
    main()
