import sys
import os
from datetime import datetime
from typing import Dict, Any
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rabbitmq_bus import RabbitMQEventBus

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
except ImportError:
    print("❌ Flask não instalado. Instale com: pip install flask flask-cors")
    sys.exit(1)


class APIGateway:

    def __init__(self, rabbitmq_host='rabbitmq', rabbitmq_port=5672):
        self.app = Flask(__name__)
        CORS(self.app) 

        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.event_bus = None

    
        self.stats_cache = {
            "battles": 0,
            "steps": 0,
            "health": {"current_hp": None, "max_hp": None},
            "position": {"current": None, "map_id": None},
            "game": {"is_running": False, "start_time": None},
            "reports": [],
            "last_update": None
        }

        self.setup_routes()

    def connect_to_rabbitmq(self):
        print("🌐 [API GATEWAY] Conectando ao RabbitMQ...")
        try:
            self.event_bus = RabbitMQEventBus(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port
            )
            print("✅ [API GATEWAY] Conectado ao RabbitMQ!")

        
            self.subscribe_to_events()
            return True
        except Exception as e:
            print(f"❌ [API GATEWAY] Erro ao conectar: {e}")
            return False

    def subscribe_to_events(self):
        self.event_bus.subscribe("battle_start", self.on_battle_start)
        self.event_bus.subscribe("step", self.on_step)
        self.event_bus.subscribe("health_change", self.on_health_change)
        self.event_bus.subscribe("position_change", self.on_position_change)
        self.event_bus.subscribe("game_start", self.on_game_start)
        self.event_bus.subscribe("game_end", self.on_game_end)
        self.event_bus.subscribe("report_generated", self.on_report_generated)


    def on_battle_start(self, data):
        self.stats_cache["battles"] += 1
        self.stats_cache["last_update"] = datetime.now().isoformat()

    def on_step(self, data):
        self.stats_cache["steps"] += 1
        self.stats_cache["last_update"] = datetime.now().isoformat()

    def on_health_change(self, data):
        self.stats_cache["health"] = {
            "current_hp": data.get("current_hp"),
            "max_hp": data.get("max_hp")
        }
        self.stats_cache["last_update"] = datetime.now().isoformat()

    def on_position_change(self, data):
        self.stats_cache["position"] = {
            "current": data.get("position"),
            "map_id": data.get("map_id")
        }
        self.stats_cache["last_update"] = datetime.now().isoformat()

    def on_game_start(self, data):
        self.stats_cache["game"] = {
            "is_running": True,
            "start_time": datetime.now().isoformat()
        }
        self.stats_cache["last_update"] = datetime.now().isoformat()

    def on_game_end(self, data):
        self.stats_cache["game"]["is_running"] = False
        self.stats_cache["last_update"] = datetime.now().isoformat()

    def on_report_generated(self, data):
        self.stats_cache["reports"].append({
            "type": data.get("type"),
            "number": data.get("number"),
            "timestamp": data.get("timestamp"),
            "stats": data.get("stats")
        })
    
        self.stats_cache["reports"] = self.stats_cache["reports"][-10:]
        self.stats_cache["last_update"] = datetime.now().isoformat()

    def setup_routes(self):

        @self.app.route('/')
        def index():
            return jsonify({
                "service": "Pokemon Event System - API Gateway",
                "version": "1.0.0",
                "endpoints": {
                    "GET /": "Esta página",
                    "GET /health": "Status de saúde da API",
                    "GET /stats": "Estatísticas do jogo",
                    "GET /stats/battles": "Estatísticas de batalhas",
                    "GET /stats/steps": "Estatísticas de passos",
                    "GET /stats/health": "Estatísticas de saúde",
                    "GET /stats/position": "Posição atual",
                    "GET /stats/game": "Status do jogo",
                    "GET /reports": "Relatórios gerados",
                    "POST /game/start": "Iniciar jogo (não implementado)",
                    "POST /game/stop": "Parar jogo (não implementado)"
                }
            })

        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "rabbitmq_connected": self.event_bus is not None
            })

        @self.app.route('/stats')
        def stats():
            return jsonify(self.stats_cache)

        @self.app.route('/stats/battles')
        def stats_battles():
            return jsonify({
                "total_battles": self.stats_cache["battles"],
                "last_update": self.stats_cache["last_update"]
            })

        @self.app.route('/stats/steps')
        def stats_steps():
            return jsonify({
                "total_steps": self.stats_cache["steps"],
                "last_update": self.stats_cache["last_update"]
            })

        @self.app.route('/stats/health')
        def stats_health():
            health_data = self.stats_cache["health"]
            percentage = 0
            if health_data["max_hp"]:
                percentage = (health_data["current_hp"] / health_data["max_hp"]) * 100

            return jsonify({
                "current_hp": health_data["current_hp"],
                "max_hp": health_data["max_hp"],
                "percentage": round(percentage, 1),
                "last_update": self.stats_cache["last_update"]
            })

        @self.app.route('/stats/position')
        def stats_position():
            return jsonify({
                "position": self.stats_cache["position"]["current"],
                "map_id": self.stats_cache["position"]["map_id"],
                "last_update": self.stats_cache["last_update"]
            })

        @self.app.route('/stats/game')
        def stats_game():
            return jsonify(self.stats_cache["game"])

        @self.app.route('/reports')
        def reports():
            return jsonify({
                "total": len(self.stats_cache["reports"]),
                "reports": self.stats_cache["reports"]
            })

        @self.app.route('/game/start', methods=['POST'])
        def game_start():
            return jsonify({
                "message": "Endpoint not implemented",
                "info": "Game service starts automatically"
            }), 501

        @self.app.route('/game/stop', methods=['POST'])
        def game_stop():
            return jsonify({
                "message": "Endpoint not implemented",
                "info": "Stop game service container to stop"
            }), 501

    def start(self, host='0.0.0.0', port=8000):
        print("=" * 70)
        print("🌐 POKEMON RED - API GATEWAY (MICROSERVICE)")
        print("=" * 70)

    
        if not self.connect_to_rabbitmq():
            print("⚠️  [API GATEWAY] Iniciando sem conexão ao RabbitMQ...")

        print(f"\n🌐 [API GATEWAY] Iniciando servidor em {host}:{port}...")
        print(f"📡 [API GATEWAY] Documentação: http://{host}:{port}/")
        print(f"📊 [API GATEWAY] Estatísticas: http://{host}:{port}/stats")
        print("\n✅ [API GATEWAY] API pronta!\n")

    
        self.app.run(host=host, port=port, debug=False)


def main():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))
    api_host = os.getenv('API_HOST', '0.0.0.0')
    api_port = int(os.getenv('API_PORT', 8000))

    gateway = APIGateway(
        rabbitmq_host=rabbitmq_host,
        rabbitmq_port=rabbitmq_port
    )

    gateway.start(host=api_host, port=api_port)


if __name__ == "__main__":
    main()
