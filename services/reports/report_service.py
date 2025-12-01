import sys
import os
import time
from datetime import datetime
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rabbitmq_bus import RabbitMQEventBus


class ReportService:

    def __init__(self, rabbitmq_host='rabbitmq', rabbitmq_port=5672, report_interval=300):
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.report_interval = report_interval
        self.event_bus = None

        self.stats = {
            "battles": {"total": 0, "history": []},
            "steps": {"total": 0, "history": []},
            "health": {"current_hp": None, "max_hp": None, "history": []},
            "position": {"current": None, "map_id": None, "history": []},
            "game": {"start_time": None, "is_running": False}
        }

        self.last_report_time = None
        self.report_count = 0

    def connect_to_rabbitmq(self):
        print("📊 [REPORT SERVICE] Conectando ao RabbitMQ...")
        try:
            self.event_bus = RabbitMQEventBus(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port
            )
            print("✅ [REPORT SERVICE] Conectado ao RabbitMQ!")
            return True
        except Exception as e:
            print(f"❌ [REPORT SERVICE] Erro ao conectar: {e}")
            return False

    def on_battle_start(self, data: Dict[str, Any]):
        self.stats["battles"]["total"] += 1
        self.stats["battles"]["history"].append({
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
        print(f"⚔️  [REPORT] Batalha #{self.stats['battles']['total']} registrada")

    def on_step(self, data: Dict[str, Any]):
        self.stats["steps"]["total"] += 1
        if self.stats["steps"]["total"] % 10 == 0:
            print(f"👣 [REPORT] {self.stats['steps']['total']} passos registrados")

    def on_health_change(self, data: Dict[str, Any]):
        self.stats["health"]["current_hp"] = data.get("current_hp")
        self.stats["health"]["max_hp"] = data.get("max_hp")

        hp_percent = 0
        if self.stats["health"]["max_hp"]:
            hp_percent = (self.stats["health"]["current_hp"] / self.stats["health"]["max_hp"]) * 100

        if hp_percent < 20:
            print(f"⚠️  [REPORT] HP Crítico: {self.stats['health']['current_hp']}/{self.stats['health']['max_hp']}")

    def on_position_change(self, data: Dict[str, Any]):

        self.stats["position"]["current"] = data.get("position")
        self.stats["position"]["map_id"] = data.get("map_id")

    def on_game_start(self, data: Dict[str, Any]):

        self.stats["game"]["start_time"] = datetime.now()
        self.stats["game"]["is_running"] = True
        self.last_report_time = datetime.now()
        print(f"🎮 [REPORT] Jogo iniciado em {self.stats['game']['start_time'].strftime('%H:%M:%S')}")

    def on_game_end(self, data: Dict[str, Any]):

        self.stats["game"]["is_running"] = False
        print("\n🏁 [REPORT] Jogo encerrado - Gerando relatório final...")
        self.generate_report(report_type="FINAL")

    def check_periodic_report(self):

        if not self.last_report_time:
            return

        current_time = datetime.now()
        elapsed = (current_time - self.last_report_time).total_seconds()

        if elapsed >= self.report_interval:
            self.generate_report(report_type="PERIÓDICO")
            self.last_report_time = current_time

    def generate_report(self, report_type="PERIÓDICO"):

        self.report_count += 1

        print("\n" + "=" * 70)
        print(f"📊 RELATÓRIO {report_type} #{self.report_count}")
        print(f"⏰ Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)


        if self.stats["game"]["start_time"]:
            play_time = (datetime.now() - self.stats["game"]["start_time"]).total_seconds()
            hours = int(play_time // 3600)
            minutes = int((play_time % 3600) // 60)
            seconds = int(play_time % 60)

            print(f"\n⏱️  TEMPO DE JOGO")
            print(f"   Tempo total: {hours:02d}:{minutes:02d}:{seconds:02d}")
            print(f"   Iniciado em: {self.stats['game']['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")


        print(f"\n👣 PASSOS")
        print(f"   Total de passos: {self.stats['steps']['total']}")


        print(f"\n⚔️  BATALHAS")
        print(f"   Total de batalhas: {self.stats['battles']['total']}")


        if self.stats["position"]["current"]:
            print(f"\n📍 POSIÇÃO ATUAL")
            print(f"   Posição: {self.stats['position']['current']}")
            print(f"   Mapa ID: {self.stats['position']['map_id']}")


        if self.stats["health"]["current_hp"] is not None:
            hp_percent = 0
            if self.stats["health"]["max_hp"]:
                hp_percent = (self.stats["health"]["current_hp"] / self.stats["health"]["max_hp"]) * 100

            print(f"\n❤️  SAÚDE")
            print(f"   HP: {self.stats['health']['current_hp']}/{self.stats['health']['max_hp']} ({hp_percent:.1f}%)")

        print("\n" + "=" * 70 + "\n")


        self.event_bus.publish("report_generated", {
            "type": report_type,
            "number": self.report_count,
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "battles": self.stats["battles"]["total"],
                "steps": self.stats["steps"]["total"],
                "health": self.stats["health"]
            }
        })

    def subscribe_to_events(self):

        print("📊 [REPORT SERVICE] Registrando subscribers...")

        self.event_bus.subscribe("battle_start", self.on_battle_start)
        self.event_bus.subscribe("step", self.on_step)
        self.event_bus.subscribe("health_change", self.on_health_change)
        self.event_bus.subscribe("position_change", self.on_position_change)
        self.event_bus.subscribe("game_start", self.on_game_start)
        self.event_bus.subscribe("game_end", self.on_game_end)

        print("✅ [REPORT SERVICE] Subscribers registrados!")

    def start(self):

        print("=" * 70)
        print("📊 POKEMON RED - REPORT SERVICE (MICROSERVICE)")
        print("=" * 70)


        if not self.connect_to_rabbitmq():
            return False


        self.subscribe_to_events()

        print(f"\n📊 [REPORT SERVICE] Relatórios a cada {self.report_interval}s")
        print("✅ [REPORT SERVICE] Serviço pronto! Aguardando eventos...\n")


        try:
            while True:
                time.sleep(10)
                self.check_periodic_report()

        except KeyboardInterrupt:
            print("\n⚠️  [REPORT SERVICE] Interrupção recebida")
        finally:
            self.stop()

        return True

    def stop(self):

        print("\n🛑 [REPORT SERVICE] Encerrando...")
        if self.event_bus:
            self.event_bus.close()
        print("✅ [REPORT SERVICE] Serviço encerrado!")


def main():

    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
    report_interval = int(os.getenv('REPORT_INTERVAL', 300))

    service = ReportService(
        rabbitmq_host=rabbitmq_host,
        rabbitmq_port=rabbitmq_port,
        report_interval=report_interval
    )

    service.start()


if __name__ == "__main__":
    main()
