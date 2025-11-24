"""
Pokemon Red - FIFO Command Mode (Ponto 4 - Dupla)
Controle via comandos do terminal ao invés de teclado.
Simula Twitter Plays Pokemon com fila FIFO de comandos.
"""

import sys
import io

# Configurar encoding UTF-8 no Windows para suportar emojis
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
    """
    Configura o sistema de eventos: cria processadores e os registra no Event Bus.

    Args:
        pyboy: Instância do PyBoy
        event_bus: Event Bus para comunicação

    Returns:
        dict: Dicionário com todos os processadores criados
    """
    # Criar processadores
    battle_counter = BattleCounter()
    step_counter = StepCounter()
    position_tracker = PositionTracker()
    time_tracker = TimeTracker()
    health_tracker = HealthTracker()

    # Criar dicionário de processadores
    processors = {
        "battles": battle_counter,
        "steps": step_counter,
        "position": position_tracker,
        "time": time_tracker,
        "health": health_tracker
    }

    # Criar gerador de relatórios (relatórios a cada 5 minutos)
    report_generator = ReportGenerator(processors, report_interval=300)
    processors["reports"] = report_generator

    # Registrar processadores no Event Bus
    event_bus.subscribe("battle_start", battle_counter.on_battle_start)
    event_bus.subscribe("step", step_counter.on_step)
    event_bus.subscribe("position_change", position_tracker.on_position_change)
    event_bus.subscribe("health_change", health_tracker.on_health_change)
    event_bus.subscribe("game_start", time_tracker.on_game_start)
    event_bus.subscribe("game_end", report_generator.on_game_end)

    # Emitir evento de início do jogo
    event_bus.publish("game_start", {})

    print("✅ Sistema de eventos configurado!")
    print(f"📊 Processadores ativos: {len(processors)}")
    print(f"   - {', '.join(processors.keys())}")

    return processors


def main():
    """Função principal - modo FIFO commands."""

    print("=" * 70)
    print("🎮 POKEMON RED - TWITTER PLAYS POKEMON MODE")
    print("=" * 70)

    # Criar Event Bus
    event_bus = EventBus()

    # Criar fila FIFO de comandos
    command_queue = CommandQueue(max_size=100)

    # Inicializar PyBoy (sem input do teclado)
    print("\n🎮 Iniciando Pokemon Red...")
    pyboy = PyBoy(
        "rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb",
        window="SDL2",
        scale=3,
        no_input=True  # IMPORTANTE: Desabilita input do teclado
    )

    # Configurar sistema de eventos
    print()
    processors = setup_event_system(pyboy, event_bus)

    # Criar monitor do jogo
    game_monitor = PokemonRedMonitor(pyboy, event_bus, debug=False)

    # Criar e iniciar handler de input do terminal
    input_handler = CommandInputHandler(command_queue)
    input_handler.start()

    # Contador de frames desde último comando
    frames_since_command = 0
    FRAMES_PER_COMMAND = 15  # Delay entre comandos (15 frames = 0.25s)

    # Loop principal do jogo
    print("\n🎮 Jogo iniciado! Digite comandos no terminal.\n")

    try:
        while pyboy.tick() and input_handler.running:
            # Atualizar monitor (detecta eventos)
            game_monitor.update()

            # Verificar se é hora de gerar relatório periódico
            processors["reports"].check_and_generate_report()

            # Processar comandos da fila FIFO
            frames_since_command += 1

            # Executar próximo comando se houver tempo suficiente desde o último
            if frames_since_command >= FRAMES_PER_COMMAND:
                next_command = command_queue.get_next_command()

                if next_command:
                    # Executar comando usando PyBoy API
                    try:
                        pyboy.button(next_command, delay=10)
                        print(f"🎮 Executando: {next_command} (fila: {command_queue.get_size()})")

                        # Emitir evento de comando executado
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
        # Parar input handler
        input_handler.stop()

        # Emitir evento de fim de jogo (gera relatório final)
        print("\n🏁 Encerrando jogo...")
        event_bus.publish("game_end", {})

        # Parar o emulador
        pyboy.stop()
        print("👋 Até logo!")


if __name__ == "__main__":
    main()
