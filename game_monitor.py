from typing import Dict, Any, Optional
from event_bus import EventBus


class PokemonRedMonitor:

    ADDR_PLAYER_X = 0xD362
    ADDR_PLAYER_Y = 0xD361
    ADDR_IN_BATTLE = 0xD057
    ADDR_DIRECTION = 0xD52A
    ADDR_MAP_ID = 0xD35E
    ADDR_PARTY_HP_CURRENT_HIGH = 0xD015
    ADDR_PARTY_HP_CURRENT_LOW = 0xD016
    ADDR_PARTY_HP_MAX_HIGH = 0xD018
    ADDR_PARTY_HP_MAX_LOW = 0xD019

    def __init__(self, pyboy, event_bus: EventBus, debug=False):
        self.pyboy = pyboy
        self.event_bus = event_bus
        self.debug = debug

        self.previous_state = {
            "position": None,
            "in_battle": None,
            "hp": None,
            "map_id": None
        }

        self.frame_count = 0
        self.debug_counter = 0

    def read_player_position(self) -> tuple:
        try:
            x = self.pyboy.memory[self.ADDR_PLAYER_X]
            y = self.pyboy.memory[self.ADDR_PLAYER_Y]
            return (x, y)
        except:
            return None

    def read_battle_status(self) -> bool:
        try:
            in_battle = self.pyboy.memory[self.ADDR_IN_BATTLE]
            return in_battle != 0
        except:
            return False

    def read_player_hp(self) -> Optional[tuple]:
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
        try:
            return self.pyboy.memory[self.ADDR_MAP_ID]
        except:
            return None

    def read_direction(self) -> Optional[int]:
        try:
            return self.pyboy.memory[self.ADDR_DIRECTION]
        except:
            return None

    def update(self) -> None:
        self.frame_count += 1

        if self.debug and self.frame_count % 60 == 0:
            pos = self.read_player_position()
            print(f"[DEBUG] Frame {self.frame_count}: Posição = {pos}")

        current_position = self.read_player_position()

        if current_position is None:
            return

        if current_position != self.previous_state["position"]:
            if self.previous_state["position"] is not None:
                if self.debug:
                    print(f"[DEBUG] PASSO DETECTADO: {self.previous_state['position']} -> {current_position}")

                self.event_bus.publish("step", {
                    "position": current_position,
                    "previous_position": self.previous_state["position"],
                    "direction": self.read_direction()
                })

            self.event_bus.publish("position_change", {
                "position": current_position,
                "map_id": self.read_map_id()
            })

            self.previous_state["position"] = current_position

        in_battle = self.read_battle_status()
        if in_battle and not self.previous_state["in_battle"]:
            self.event_bus.publish("battle_start", {
                "position": current_position,
                "map_id": self.read_map_id()
            })
        elif not in_battle and self.previous_state["in_battle"]:
            self.event_bus.publish("battle_end", {
                "position": current_position
            })

        self.previous_state["in_battle"] = in_battle

        if self.frame_count % 30 == 0:
            hp_data = self.read_player_hp()
            if hp_data and hp_data != self.previous_state["hp"]:
                current_hp, max_hp = hp_data
                if current_hp > 0:
                    self.event_bus.publish("health_change", {
                        "current_hp": current_hp,
                        "max_hp": max_hp,
                        "previous_hp": self.previous_state["hp"][0] if self.previous_state["hp"] else None
                    })
                    self.previous_state["hp"] = hp_data


class GenericGameMonitor:

    def __init__(self, pyboy, event_bus: EventBus):
        self.pyboy = pyboy
        self.event_bus = event_bus
        self.frame_count = 0
        self.previous_screen_hash = None

    def update(self) -> None:
        self.frame_count += 1

        if self.frame_count % 60 == 0:
            try:
                screen = self.pyboy.screen.ndarray
                current_hash = hash(screen.tobytes())

                if current_hash != self.previous_screen_hash:
                    self.event_bus.publish("screen_change", {
                        "frame": self.frame_count
                    })
                    self.previous_screen_hash = current_hash
            except:
                pass
