from app.application.ports import GetOptSimplesNacionalPort
from app.domain.value_objects import CNPJ
from app.infra.selenium.routines import get_opt_simples

class GetOptSimplesNacionalWithSelenium(GetOptSimplesNacionalPort):
    def get(self, cnpj: CNPJ) -> bool:
        return get_opt_simples(cnpj.value)