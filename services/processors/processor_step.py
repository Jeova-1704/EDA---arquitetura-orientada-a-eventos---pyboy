import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rabbitmq_bus import RabbitMQEventBus


class StepProcessor:

    def __init__(self):
        self.step_count = 0
        self.steps = []

    def on_step(self, data):
        self.step_count += 1
        self.steps.append({
            "step_number": self.step_count,
            "timestamp": datetime.now().isoformat(),
            "position": data.get("position"),
            "direction": data.get("direction")
        })

        
        if self.step_count % 10 == 0:
            print(f"👣 [STEP PROCESSOR] {self.step_count} passos dados "
                  f"(posição atual: {data.get('position')})")


def main():
    print("=" * 70)
    print("👣 STEP PROCESSOR SERVICE")
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

    
    processor = StepProcessor()

    
    print("📡 Registrando subscriber para 'step'...")
    event_bus.subscribe("step", processor.on_step)
    print("✅ Subscriber registrado!")

    print("\n👣 [STEP PROCESSOR] Pronto! Aguardando eventos de movimento...")
    print("💡 Pressione Ctrl+C para encerrar\n")

    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando Step Processor...")
        event_bus.close()
        print(f"📊 Total de passos processados: {processor.step_count}")
        print("✅ Serviço encerrado!")


if __name__ == "__main__":
    main()
