from dataclasses import dataclass

from app.infra.adapters import GetOptSimplesNacionalWithSelenium


@dataclass
class AdapterProvider:
    def get_get_opt_simples_nacional_with_selenium_adapter(self) -> GetOptSimplesNacionalWithSelenium:
        return GetOptSimplesNacionalWithSelenium()

    