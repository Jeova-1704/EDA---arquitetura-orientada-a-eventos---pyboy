import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rabbitmq_bus import RabbitMQEventBus


class HealthProcessor:

    def __init__(self):
        self.health_events = []
        self.current_hp = None
        self.max_hp = None

    def on_health_change(self, data):
        self.current_hp = data.get("current_hp")
        self.max_hp = data.get("max_hp")

        
        percentage = 0
        if self.max_hp and self.max_hp > 0:
            percentage = (self.current_hp / self.max_hp) * 100

        
        self.health_events.append({
            "timestamp": datetime.now().isoformat(),
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "percentage": percentage
        })

        
        print(f"❤️  [HEALTH PROCESSOR] HP: {self.current_hp}/{self.max_hp} ({percentage:.1f}%)")

        
        if percentage < 20:
            print(f"⚠️  [HEALTH PROCESSOR] ⚠️  HP CRÍTICO! ⚠️  "
                  f"{self.current_hp}/{self.max_hp} ({percentage:.1f}%)")


def main():
    print("=" * 70)
    print("❤️  HEALTH PROCESSOR SERVICE")
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

    
    processor = HealthProcessor()

    
    print("📡 Registrando subscriber para 'health_change'...")
    event_bus.subscribe("health_change", processor.on_health_change)
    print("✅ Subscriber registrado!")

    print("\n❤️  [HEALTH PROCESSOR] Pronto! Monitorando saúde do Pokemon...")
    print("💡 Pressione Ctrl+C para encerrar\n")

    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando Health Processor...")
        event_bus.close()
        print(f"📊 Total de eventos de saúde: {len(processor.health_events)}")
        if processor.current_hp:
            print(f"📊 HP Final: {processor.current_hp}/{processor.max_hp}")
        print("✅ Serviço encerrado!")


if __name__ == "__main__":
    main()
