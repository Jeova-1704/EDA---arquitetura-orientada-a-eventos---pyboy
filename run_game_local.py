import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from services.game.game_service import GameService


def main():
    print("=" * 70)
    print("🎮 POKEMON RED - MODO LOCAL COM INTERFACE GRÁFICA")
    print("=" * 70)
    print("📋 PRÉ-REQUISITOS:")
    print("   1. RabbitMQ rodando: docker compose up -d rabbitmq")
    print("   2. ROM em: rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb")
    print()
    print("=" * 70)
    print()

    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
    rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
    rom_path = os.getenv('ROM_PATH', 'rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb')
    service = GameService(
        rabbitmq_host=rabbitmq_host,
        rabbitmq_port=rabbitmq_port
    )

    service.start(rom_path, headless=False)

if __name__ == "__main__":
    main()
