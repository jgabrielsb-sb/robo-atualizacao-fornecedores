from dataclasses import dataclass

from app.composition.adapter import AdapterProvider
from app.composition.infra import InfraProvider

@dataclass
class Container:
    def __init__(self):
        self.adapter_provider = AdapterProvider()
        self.infra_provider = InfraProvider()
