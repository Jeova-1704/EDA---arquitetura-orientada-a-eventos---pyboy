from datetime import datetime
from typing import Dict, Any


class BattleCounter:
    """Processador que conta o número de batalhas."""

    def __init__(self):
        self.battle_count = 0
        self.battles = []

    def on_battle_start(self, data: Dict[str, Any]) -> None:
        """Chamado quando uma batalha inicia."""
        self.battle_count += 1
        self.battles.append({
            "battle_number": self.battle_count,
            "timestamp": datetime.now(),
            "data": data
        })
        print(f"⚔️  Batalha #{self.battle_count} iniciada!")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de batalhas."""
        return {
            "total_battles": self.battle_count,
            "battles": self.battles
        }


class StepCounter:
    """Processador que conta passos do jogador."""

    def __init__(self):
        self.step_count = 0
        self.steps = []

    def on_step(self, data: Dict[str, Any]) -> None:
        """Chamado quando o jogador dá um passo."""
        self.step_count += 1
        self.steps.append({
            "step_number": self.step_count,
            "timestamp": datetime.now(),
            "position": data.get("position"),
            "direction": data.get("direction")
        })

        if self.step_count % 10 == 0:
            print(f"👣 {self.step_count} passos dados")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de passos."""
        return {
            "total_steps": self.step_count,
            "recent_steps": self.steps[-10:] if len(self.steps) > 10 else self.steps
        }


class PositionTracker:
    """Processador que rastreia a posição do jogador."""

    def __init__(self):
        self.positions = []
        self.current_position = None

    def on_position_change(self, data: Dict[str, Any]) -> None:
        """Chamado quando a posição do jogador muda."""
        self.current_position = data.get("position")
        self.positions.append({
            "timestamp": datetime.now(),
            "position": self.current_position,
            "map_id": data.get("map_id")
        })

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de posição."""
        return {
            "current_position": self.current_position,
            "position_history": self.positions[-20:] if len(self.positions) > 20 else self.positions
        }


class TimeTracker:
    """Processador que rastreia tempo de jogo."""

    def __init__(self):
        self.start_time = datetime.now()
        self.pause_time = None
        self.total_paused_time = 0

    def on_game_start(self, data: Dict[str, Any]) -> None:
        """Chamado quando o jogo inicia."""
        self.start_time = datetime.now()
        print(f"🎮 Jogo iniciado às {self.start_time.strftime('%H:%M:%S')}")

    def on_game_pause(self, data: Dict[str, Any]) -> None:
        """Chamado quando o jogo é pausado."""
        self.pause_time = datetime.now()

    def on_game_resume(self, data: Dict[str, Any]) -> None:
        """Chamado quando o jogo é resumido."""
        if self.pause_time:
            pause_duration = (datetime.now() - self.pause_time).total_seconds()
            self.total_paused_time += pause_duration
            self.pause_time = None

    def get_play_time(self) -> float:
        """Retorna tempo de jogo em segundos (excluindo pausas)."""
        total_time = (datetime.now() - self.start_time).total_seconds()
        return total_time - self.total_paused_time

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de tempo."""
        play_time = self.get_play_time()
        hours = int(play_time // 3600)
        minutes = int((play_time % 3600) // 60)
        seconds = int(play_time % 60)

        return {
            "play_time_seconds": play_time,
            "play_time_formatted": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }


class HealthTracker:
    """Processador que rastreia HP do Pokémon."""

    def __init__(self):
        self.health_events = []
        self.current_hp = None
        self.max_hp = None

    def on_health_change(self, data: Dict[str, Any]) -> None:
        """Chamado quando o HP muda."""
        self.current_hp = data.get("current_hp")
        self.max_hp = data.get("max_hp")
        self.health_events.append({
            "timestamp": datetime.now(),
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "percentage": (self.current_hp / self.max_hp * 100) if self.max_hp else 0
        })

        if self.current_hp and self.max_hp:
            percentage = (self.current_hp / self.max_hp) * 100
            if percentage < 20:
                print(f"⚠️  HP crítico: {self.current_hp}/{self.max_hp} ({percentage:.1f}%)")

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de saúde."""
        return {
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "health_percentage": (self.current_hp / self.max_hp * 100) if (self.current_hp and self.max_hp) else 0,
            "recent_events": self.health_events[-10:] if len(self.health_events) > 10 else self.health_events
        }


class ReportGenerator:
    """Processador que gera relatórios periódicos."""

    def __init__(self, processors: Dict[str, Any], report_interval: int = 300):
        """
        Args:
            processors: Dicionário com todos os processadores
            report_interval: Intervalo em segundos entre relatórios (padrão: 5 minutos)
        """
        self.processors = processors
        self.report_interval = report_interval
        self.last_report_time = datetime.now()
        self.report_count = 0

    def check_and_generate_report(self) -> None:
        """Verifica se é hora de gerar um relatório periódico."""
        current_time = datetime.now()
        elapsed = (current_time - self.last_report_time).total_seconds()

        if elapsed >= self.report_interval:
            self.generate_report(report_type="periodic")
            self.last_report_time = current_time

    def generate_report(self, report_type: str = "final") -> None:
        """Gera um relatório completo com todas as estatísticas."""
        self.report_count += 1

        print("\n" + "=" * 70)
        print(f"📊 RELATÓRIO {report_type.upper()} #{self.report_count}")
        print(f"⏰ Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # Tempo de jogo
        if "time" in self.processors:
            time_stats = self.processors["time"].get_stats()
            print(f"\n⏱️  TEMPO DE JOGO")
            print(f"   Tempo total: {time_stats['play_time_formatted']}")
            print(f"   Iniciado em: {time_stats['start_time']}")

        # Passos
        if "steps" in self.processors:
            step_stats = self.processors["steps"].get_stats()
            print(f"\n👣 PASSOS")
            print(f"   Total de passos: {step_stats['total_steps']}")

        # Batalhas
        if "battles" in self.processors:
            battle_stats = self.processors["battles"].get_stats()
            print(f"\n⚔️  BATALHAS")
            print(f"   Total de batalhas: {battle_stats['total_battles']}")

        # HP
        if "health" in self.processors:
            health_stats = self.processors["health"].get_stats()
            if health_stats["current_hp"] is not None:
                print(f"\n❤️  SAÚDE")
                print(f"   HP: {health_stats['current_hp']}/{health_stats['max_hp']} " +
                      f"({health_stats['health_percentage']:.1f}%)")

        print("\n" + "=" * 70 + "\n")

    def on_game_end(self, data: Dict[str, Any]) -> None:
        """Chamado quando o jogo termina."""
        self.generate_report(report_type="final")
