import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from pyboy import PyBoy
from rabbitmq_bus import RabbitMQEventBus
from game_monitor import PokemonRedMonitor


class GameService:

    def __init__(self, rabbitmq_host='rabbitmq', rabbitmq_port=5672):
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.event_bus = None
        self.pyboy = None
        self.monitor = None
        self.running = False

    def connect_to_rabbitmq(self):
        print("🎮 [GAME SERVICE] Conectando ao RabbitMQ...")
        try:
            self.event_bus = RabbitMQEventBus(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port
            )
            print("✅ [GAME SERVICE] Conectado ao RabbitMQ!")
            return True
        except Exception as e:
            print(f"❌ [GAME SERVICE] Erro ao conectar ao RabbitMQ: {e}")
            return False

    def initialize_emulator(self, rom_path, headless=False):
        print(f"🎮 [GAME SERVICE] Carregando ROM: {rom_path}")
        try:
            if headless:
            
                self.pyboy = PyBoy(
                    rom_path,
                    window="null", 
                )
                print("✅ [GAME SERVICE] Emulador inicializado (modo headless)!")
            else:
            
                self.pyboy = PyBoy(
                    rom_path,
                    window="SDL2", 
                    scale=3 
                )
                print("✅ [GAME SERVICE] Emulador inicializado (modo gráfico)!")
                print("🎮 [GAME SERVICE] Use o teclado para jogar:")
                print("   Setas: Movimento | Z: A | X: B | Enter: Start | Backspace: Select")
            return True
        except Exception as e:
            print(f"❌ [GAME SERVICE] Erro ao inicializar emulador: {e}")
            return False

    def initialize_monitor(self):
        print("🎮 [GAME SERVICE] Inicializando monitor...")
        try:
            self.monitor = PokemonRedMonitor(
                self.pyboy,
                self.event_bus,
                debug=False
            )
            print("✅ [GAME SERVICE] Monitor inicializado!")
            return True
        except Exception as e:
            print(f"❌ [GAME SERVICE] Erro ao inicializar monitor: {e}")
            return False

    def start(self, rom_path, headless=False):
        print("=" * 70)
        print("🎮 POKEMON RED - GAME SERVICE (MICROSERVICE)")
        print("=" * 70)

    
        if not self.connect_to_rabbitmq():
            return False

    
        if not self.initialize_emulator(rom_path, headless=headless):
            return False

    
        if not self.initialize_monitor():
            return False

    
        self.event_bus.publish("game_start", {
            "timestamp": time.time(),
            "service": "game"
        })

        print("\n🎮 [GAME SERVICE] Iniciando game loop...")
        if headless:
            print("💡 [GAME SERVICE] Emulador rodando em modo headless")
        else:
            print("💡 [GAME SERVICE] Emulador rodando com interface gráfica")
        print("💡 [GAME SERVICE] Eventos sendo publicados no RabbitMQ\n")

    
        self.running = True
        frame_count = 0

        try:
            while self.pyboy.tick() and self.running:
                frame_count += 1
                self.monitor.update()


        except KeyboardInterrupt:
            print("\n⚠️  [GAME SERVICE] Interrupção recebida")
        except Exception as e:
            print(f"\n❌ [GAME SERVICE] Erro no game loop: {e}")
        finally:
            self.stop()

        return True

    def stop(self):
        print("\n🛑 [GAME SERVICE] Encerrando...")
        self.running = False

    
        if self.event_bus:
            self.event_bus.publish("game_end", {
                "timestamp": time.time(),
                "service": "game"
            })
            time.sleep(1) 
            self.event_bus.close()

    
        if self.pyboy:
            self.pyboy.stop()

        print("✅ [GAME SERVICE] Serviço encerrado!")


def main():

    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
    rom_path = os.getenv('ROM_PATH', '/app/rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb')

    headless = os.getenv('HEADLESS', 'false').lower() == 'true'

    print(f"🎮 [CONFIG] Modo: {'Headless' if headless else 'Interface Gráfica (SDL2)'}")
    print(f"🎮 [CONFIG] RabbitMQ: {rabbitmq_host}:{rabbitmq_port}")
    print(f"🎮 [CONFIG] ROM: {rom_path}")


    service = GameService(
        rabbitmq_host=rabbitmq_host,
        rabbitmq_port=rabbitmq_port
    )

    service.start(rom_path, headless=headless)


if __name__ == "__main__":
    main()
