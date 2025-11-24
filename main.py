import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from pyboy import PyBoy
from event_bus import EventBus
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

    event_bus.subscribe("battle_start", battle_counter.on_battle_start)
    event_bus.subscribe("step", step_counter.on_step)
    event_bus.subscribe("position_change", position_tracker.on_position_change)
    event_bus.subscribe("health_change", health_tracker.on_health_change)
    event_bus.subscribe("game_start", time_tracker.on_game_start)
    event_bus.subscribe("game_end", report_generator.on_game_end)

    event_bus.publish("game_start", {})

    print("✅ Sistema de eventos configurado!")
    print(f"📊 Processadores ativos: {len(processors)}")
    print(f"   - {', '.join(processors.keys())}")
    print("\n🎮 Controles: Use o teclado para jogar")
    print("   Setas: Movimento | Z: A | X: B | Enter: Start | Backspace: Select")
    print("   ESC: Fechar jogo\n")

    return processors


def main():

    event_bus = EventBus()

    print("🎮 Iniciando Pokemon Red...")
    pyboy = PyBoy(
        "rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb",
        window="SDL2",
        scale=3
    )

    processors = setup_event_system(pyboy, event_bus)

    game_monitor = PokemonRedMonitor(pyboy, event_bus, debug=False)

    try:
        while pyboy.tick():
            game_monitor.update()

            processors["reports"].check_and_generate_report()

    except KeyboardInterrupt:
        print("\n\n⚠️  Jogo interrompido pelo usuário")

    finally:
        print("\n🏁 Encerrando jogo...")
        event_bus.publish("game_end", {})

        pyboy.stop()
        print("👋 Até logo!")


if __name__ == "__main__":
    main()
