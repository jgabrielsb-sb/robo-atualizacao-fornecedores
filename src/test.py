from app.composition.container import Container
from config.settings import settings

container = Container()
adapter = container.adapter_provider.get_get_fornecedores_to_update_via_fornecedores_api_adapter()

if __name__ == "__main__":
    fornecedores = adapter.get()
    print(fornecedores)

        
