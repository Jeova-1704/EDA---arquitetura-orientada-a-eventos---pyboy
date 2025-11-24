"""
Pokemon Red - Sistema de Eventos Orientado a Arquitetura
Main script com integração do Event Bus, processadores e monitor do jogo.
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
    print("\n🎮 Controles: Use o teclado para jogar")
    print("   Setas: Movimento | Z: A | X: B | Enter: Start | Backspace: Select")
    print("   ESC: Fechar jogo\n")

    return processors


def main():
    """Função principal que executa o emulador com o sistema de eventos."""

    # Criar Event Bus
    event_bus = EventBus()

    # Inicializar PyBoy
    print("🎮 Iniciando Pokemon Red...")
    pyboy = PyBoy(
        "rom/Pokemon - Red Version (USA, Europe) (SGB Enhanced).gb",
        window="SDL2",
        scale=3
    )

    # Configurar sistema de eventos
    processors = setup_event_system(pyboy, event_bus)

    # Criar monitor do jogo
    game_monitor = PokemonRedMonitor(pyboy, event_bus, debug=False)

    # Loop principal do jogo
    try:
        while pyboy.tick():
            # Atualizar monitor (detecta eventos)
            game_monitor.update()

            # Verificar se é hora de gerar relatório periódico
            processors["reports"].check_and_generate_report()

    except KeyboardInterrupt:
        print("\n\n⚠️  Jogo interrompido pelo usuário")

    finally:
        # Emitir evento de fim de jogo (gera relatório final)
        print("\n🏁 Encerrando jogo...")
        event_bus.publish("game_end", {})

        # Parar o emulador
        pyboy.stop()
        print("👋 Até logo!")


if __name__ == "__main__":
    main()
