from dataclasses import dataclass, field
from typing import Any


@dataclass
class EventDispatcherService:
    handlers: list = field(default_factory=list)

    def register(self, handler: Any) -> None:
        self.handlers.append(handler)

    def dispatch(self, event: Any) -> None:
        for handler in self.handlers:
            handler.handle(event)
