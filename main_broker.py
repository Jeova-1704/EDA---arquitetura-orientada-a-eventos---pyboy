import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from pyboy import PyBoy
from rabbitmq_bus import RabbitMQEventBus
from event_processors import (
    BattleCounter,
    StepCounter,
    PositionTracker,
    TimeTracker,
    HealthTracker,
    ReportGenerator
)
from game_monitor import PokemonRedMonitor


def setup_event_system(pyboy, event_bus):
    print("\n📊 Configurando sistema de eventos...")

    battle_counter = BattleCounter()
    step_counter = StepCounter()
    position_tracker = PositionTracker()
    time_tracker = TimeTracker()
    health_tracker = HealthTracker()

    processors = {
        "battles": battle_counter,
        "steps": step_counter,
        "position": position_tracker,
        "time": time_tracker,
        "health": health_tracker
    }

    report_generator = ReportGenerator(processors, report_interval=300)
    processors["reports"] = report_generator

    print("📝 Registrando subscribers no RabbitMQ...")

    event_bus.subscribe("battle_start", battle_counter.on_battle_start)
    event_bus.subscribe("step", step_counter.on_step)
    event_bus.subscribe("position_change", position_tracker.on_position_change)
    event_bus.subscribe("health_change", health_tracker.on_health_change)
    event_bus.subscribe("game_start", time_tracker.on_game_start)
    event_bus.subscribe("game_end", report_generator.on_game_end)

    import time
    time.sleep(1)

    event_bus.publish("game_start", {})

    print("✅ Sistema de eventos configurado!")
    print(f"📊 Processadores ativos: {len(processors)}")
    print(f"   - {', '.join(processors.keys())}")
    print("\n🎮 Controles: Use o teclado para jogar")
    print("   Setas: Movimento | Z: A | X: B | Enter: Start | Backspace: Select")
    print("   ESC: Fechar jogo\n")

    return processors


def main():

    print("=" * 70)
    print("🎮 POKEMON RED - RABBITMQ BROKER MODE")
    print("=" * 70)
    print("\n🐰 Usando RabbitMQ como broker de eventos")
    print("💡 Arquitetura distribuída com mensageria profissional\n")

    try:
        event_bus = RabbitMQEventBus(host='localhost', port=5672)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\n💡 SOLUÇÃO:")
        print("1. Certifique-se de que o RabbitMQ está rodando:")
        print("   docker-compose up -d")
        print("\n2. Ou instale o RabbitMQ localmente")
        print("3. Aguarde alguns segundos e tente novamente\n")
        return

    print("\n🎮 Iniciando Pokemon Red...")
    pyboy = PyBoy(
        "rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb",
        window="SDL2",
        scale=3
    )

    processors = setup_event_system(pyboy, event_bus)

    game_monitor = PokemonRedMonitor(pyboy, event_bus, debug=False)

    print("🎮 Jogo iniciado!\n")

    try:
        while pyboy.tick():
            game_monitor.update()

            processors["reports"].check_and_generate_report()

    except KeyboardInterrupt:
        print("\n\n⚠️  Jogo interrompido pelo usuário (Ctrl+C)")

    finally:
        print("\n🏁 Encerrando jogo...")
        event_bus.publish("game_end", {})

        import time
        time.sleep(2)

        event_bus.close()

        pyboy.stop()
        print("👋 Até logo!")


if __name__ == "__main__":
    main()
