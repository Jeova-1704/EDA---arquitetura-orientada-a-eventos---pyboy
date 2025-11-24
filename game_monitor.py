"""
Game Monitor - Monitora o estado do jogo Pokemon Red e emite eventos.
Detecta mudanças na memória do jogo e publica eventos correspondentes.
"""

from typing import Dict, Any, Optional
from event_bus import EventBus


class PokemonRedMonitor:
    """
    Monitor para Pokemon Red que detecta eventos do jogo através da memória.

    Endereços de memória importantes para Pokemon Red:
    - 0xD355: Player X position
    - 0xD356: Player Y position
    - 0xD057: In battle flag (0 = overworld, 1 = battle)
    - 0xD163: Player facing direction
    - 0xD16B: Current map ID
    - 0xD015: Party Pokemon 1 Current HP (high byte)
    - 0xD016: Party Pokemon 1 Current HP (low byte)
    - 0xD018: Party Pokemon 1 Max HP (high byte)
    - 0xD019: Party Pokemon 1 Max HP (low byte)

    Passos são detectados por mudança de posição (X, Y).
    """

    # Endereços de memória
    # Tentando múltiplos endereços conhecidos para posição
    ADDR_PLAYER_X = 0xD362  # X position in map
    ADDR_PLAYER_Y = 0xD361  # Y position in map
    ADDR_IN_BATTLE = 0xD057
    ADDR_DIRECTION = 0xD52A  # Direction the player is facing
    ADDR_MAP_ID = 0xD35E
    ADDR_PARTY_HP_CURRENT_HIGH = 0xD015
    ADDR_PARTY_HP_CURRENT_LOW = 0xD016
    ADDR_PARTY_HP_MAX_HIGH = 0xD018
    ADDR_PARTY_HP_MAX_LOW = 0xD019

    def __init__(self, pyboy, event_bus: EventBus, debug=False):
        """
        Args:
            pyboy: Instância do PyBoy
            event_bus: Event Bus para publicar eventos
            debug: Se True, mostra informações de debug
        """
        self.pyboy = pyboy
        self.event_bus = event_bus
        self.debug = debug

        # Estado anterior do jogo
        self.previous_state = {
            "position": None,
            "in_battle": None,
            "hp": None,
            "map_id": None
        }

        # Contador de frames para controlar frequência de verificações
        self.frame_count = 0
        self.debug_counter = 0

    def read_player_position(self) -> tuple:
        """Lê a posição atual do jogador."""
        try:
            x = self.pyboy.memory[self.ADDR_PLAYER_X]
            y = self.pyboy.memory[self.ADDR_PLAYER_Y]
            return (x, y)
        except:
            return None

    def read_battle_status(self) -> bool:
        """Verifica se está em batalha."""
        try:
            in_battle = self.pyboy.memory[self.ADDR_IN_BATTLE]
            return in_battle != 0
        except:
            return False

    def read_player_hp(self) -> Optional[tuple]:
        """Lê HP atual e máximo do primeiro Pokémon."""
        try:
            current_high = self.pyboy.memory[self.ADDR_PARTY_HP_CURRENT_HIGH]
            current_low = self.pyboy.memory[self.ADDR_PARTY_HP_CURRENT_LOW]
            max_high = self.pyboy.memory[self.ADDR_PARTY_HP_MAX_HIGH]
            max_low = self.pyboy.memory[self.ADDR_PARTY_HP_MAX_LOW]

            current_hp = (current_high << 8) | current_low
            max_hp = (max_high << 8) | max_low

            return (current_hp, max_hp)
        except:
            return None

    def read_map_id(self) -> Optional[int]:
        """Lê o ID do mapa atual."""
        try:
            return self.pyboy.memory[self.ADDR_MAP_ID]
        except:
            return None

    def read_direction(self) -> Optional[int]:
        """Lê a direção que o jogador está olhando."""
        try:
            return self.pyboy.memory[self.ADDR_DIRECTION]
        except:
            return None

    def update(self) -> None:
        """
        Atualiza o monitor e detecta mudanças no estado do jogo.
        Deve ser chamado a cada frame.
        """
        self.frame_count += 1

        # Debug: mostrar posição a cada 60 frames (1 segundo)
        if self.debug and self.frame_count % 60 == 0:
            pos = self.read_player_position()
            print(f"[DEBUG] Frame {self.frame_count}: Posição = {pos}")

        # Verificar mudança de posição para detectar passos REAIS
        current_position = self.read_player_position()

        if current_position is None:
            return  # Não conseguiu ler posição, pular este frame

        # Verificar se houve mudança de posição
        if current_position != self.previous_state["position"]:
            # Só emitir evento de passo se já tínhamos uma posição anterior válida
            if self.previous_state["position"] is not None:
                if self.debug:
                    print(f"[DEBUG] PASSO DETECTADO: {self.previous_state['position']} -> {current_position}")

                self.event_bus.publish("step", {
                    "position": current_position,
                    "previous_position": self.previous_state["position"],
                    "direction": self.read_direction()
                })

            # Atualizar posição para tracking
            self.event_bus.publish("position_change", {
                "position": current_position,
                "map_id": self.read_map_id()
            })

            # Atualizar posição anterior
            self.previous_state["position"] = current_position

        # Verificar status de batalha
        in_battle = self.read_battle_status()
        if in_battle and not self.previous_state["in_battle"]:
            # Batalha iniciou
            self.event_bus.publish("battle_start", {
                "position": current_position,
                "map_id": self.read_map_id()
            })
        elif not in_battle and self.previous_state["in_battle"]:
            # Batalha terminou
            self.event_bus.publish("battle_end", {
                "position": current_position
            })

        self.previous_state["in_battle"] = in_battle

        # Verificar HP (a cada 30 frames para não verificar muito frequentemente)
        if self.frame_count % 30 == 0:
            hp_data = self.read_player_hp()
            if hp_data and hp_data != self.previous_state["hp"]:
                current_hp, max_hp = hp_data
                if current_hp > 0:  # Só emitir se HP válido
                    self.event_bus.publish("health_change", {
                        "current_hp": current_hp,
                        "max_hp": max_hp,
                        "previous_hp": self.previous_state["hp"][0] if self.previous_state["hp"] else None
                    })
                    self.previous_state["hp"] = hp_data


class GenericGameMonitor:
    """
    Monitor genérico que pode ser usado quando não houver um monitor específico.
    Detecta mudanças básicas na tela.
    """

    def __init__(self, pyboy, event_bus: EventBus):
        self.pyboy = pyboy
        self.event_bus = event_bus
        self.frame_count = 0
        self.previous_screen_hash = None

    def update(self) -> None:
        """Atualiza o monitor genérico."""
        self.frame_count += 1

        # A cada 60 frames (aproximadamente 1 segundo)
        if self.frame_count % 60 == 0:
            try:
                # Pegar hash simples da tela para detectar mudanças
                screen = self.pyboy.screen.ndarray
                current_hash = hash(screen.tobytes())

                if current_hash != self.previous_screen_hash:
                    self.event_bus.publish("screen_change", {
                        "frame": self.frame_count
                    })
                    self.previous_screen_hash = current_hash
            except:
                pass
