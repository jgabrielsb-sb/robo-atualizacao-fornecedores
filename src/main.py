from app.composition.adapter import AdapterProvider
from app.composition.infra import InfraProvider
from app.domain.value_objects import CNPJ

adapter_provider = AdapterProvider()
infra_provider = InfraProvider()

receita_api_requester = infra_provider.get_receita_api_requester()
print(receita_api_requester.get_company(CNPJ("28738609000181")))