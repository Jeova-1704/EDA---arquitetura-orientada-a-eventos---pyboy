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
from command_queue import CommandQueue
from command_input import CommandInputHandler
import time


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

    return processors


def main():

    print("=" * 70)
    print("🎮 POKEMON RED - TWITTER PLAYS POKEMON MODE")
    print("=" * 70)

    event_bus = EventBus()

    command_queue = CommandQueue(max_size=100)

    print("\n🎮 Iniciando Pokemon Red...")
    pyboy = PyBoy(
        "rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb",
        window="SDL2",
        scale=3,
        no_input=True
    )

    print()
    processors = setup_event_system(pyboy, event_bus)

    game_monitor = PokemonRedMonitor(pyboy, event_bus, debug=False)

    input_handler = CommandInputHandler(command_queue)
    input_handler.start()

    frames_since_command = 0
    FRAMES_PER_COMMAND = 15

    print("\n🎮 Jogo iniciado! Digite comandos no terminal.\n")

    try:
        while pyboy.tick() and input_handler.running:
            game_monitor.update()

            processors["reports"].check_and_generate_report()

            frames_since_command += 1

            if frames_since_command >= FRAMES_PER_COMMAND:
                next_command = command_queue.get_next_command()

                if next_command:
                    try:
                        pyboy.button(next_command, delay=10)
                        print(f"🎮 Executando: {next_command} (fila: {command_queue.get_size()})")

                        event_bus.publish("command_executed", {
                            "command": next_command,
                            "queue_size": command_queue.get_size()
                        })

                        frames_since_command = 0
                    except Exception as e:
                        print(f"❌ Erro ao executar comando '{next_command}': {e}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Jogo interrompido pelo usuário (Ctrl+C)")

    finally:
        input_handler.stop()

        print("\n🏁 Encerrando jogo...")
        event_bus.publish("game_end", {})

        pyboy.stop()
        print("👋 Até logo!")


if __name__ == "__main__":
    main()
