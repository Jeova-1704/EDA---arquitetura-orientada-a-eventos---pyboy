from typing import Callable, Dict, List, Any
from collections import defaultdict


class EventBus:

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

    def publish(self, event_type: str, data: Any = None) -> None:
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(data)

    def clear(self) -> None:
        self._subscribers.clear()
