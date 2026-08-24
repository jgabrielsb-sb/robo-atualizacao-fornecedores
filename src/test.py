from app.composition.container import Container
from app.domain.value_objects import CNPJ

CNPJ = CNPJ.create(cnpj='04829913000176')
container = Container()
get_opt_simples_nacional_port = container.adapter_provider.get_get_opt_simples_nacional_with_selenium_adapter()
opt_simples_nacional = get_opt_simples_nacional_port.get(CNPJ)
print(opt_simples_nacional)