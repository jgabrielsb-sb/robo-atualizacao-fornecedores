import requests
from pydantic import BaseModel

from app.domain.value_objects import CNPJ, CodigoMunicipioIBGE

class EmpresaResponse(BaseModel):
    municipio_code: CodigoMunicipioIBGE
    municipio: str

    opt_simples_nacional: bool
    razao_social: str 
    nome_fantasia: str | None = None
    endereco: str 
    numero: str 
    complemento: str | None = None
    cep: str 
    bairro: str 
    uf: str 
    ddd: str 
    natureza_juridica: str 
    atividade_economica_principal: str 
    atividade_economica_code: str 

class CNPJJAAPIRequester:
    def __init__(
        self, 
        api_key: str | None = None, 
        max_age: int | None = None,
        env: str = "dev" # dev or prod
    ):
        self._env = env

        if env == "prod":
            if api_key is None or max_age is None:
                raise ValueError("API key and max_age are required for production environment")
            
            self._headers = {
                "Authorization": f"{api_key}",
                "max-age": str(max_age)
            }
            self._base_url = "https://api.cnpja.com"
        elif env == "dev":
            self._headers = None
            self._base_url = "https://open.cnpja.com"
        else:
            raise ValueError(f"Invalid environment. Must be 'dev' or 'prod', but got {env}")

    def get(self, cnpj: CNPJ) -> EmpresaResponse:
        if self._env == "prod":
            url = f"{self._base_url}/office/{cnpj.value}?simples=true"
            
            response = requests.get(url, headers=self._headers)
            data = response.json()
        else:
            url = f"{self._base_url}/office/{cnpj.value}"
            response = requests.get(url)
            data = response.json()

        response = requests.get(url, headers=self._headers)
        data = response.json()
        print(data)

        fornecedor_data = {
            "municipio_code": str(data.get("address", {}).get("municipality")),
            "municipio": data.get("address", {}).get("city"),
            "opt_simples_nacional": data.get("company", {}).get("simples", {}).get("optant"),
            "razao_social": data.get("company", {}).get("name"),
            "nome_fantasia": data.get("alias"),
            "endereco": data.get("address", {}).get("street"),
            "numero": data.get("address", {}).get("number"),
            "complemento": data.get("address", {}).get("details"),
            "cep": data.get("address", {}).get("zip"),
            "bairro": data.get("address", {}).get("district"),
            "uf": data.get("address", {}).get("state"),
            "ddd": data.get("phones", [{}])[0].get("area"),
            "natureza_juridica": data.get("company", {}).get("nature", {}).get("text"),
            "atividade_economica_principal": data.get("mainActivity", {}).get("text"),
            "atividade_economica_code": str(data.get("mainActivity", {}).get("id"))
        }
        
        return EmpresaResponse(
            municipio_code=CodigoMunicipioIBGE.create(fornecedor_data["municipio_code"]),
            municipio=fornecedor_data["municipio"],
            opt_simples_nacional=fornecedor_data["opt_simples_nacional"],
            razao_social=fornecedor_data["razao_social"],
            nome_fantasia=fornecedor_data["nome_fantasia"],
            endereco=fornecedor_data["endereco"],
            numero=fornecedor_data["numero"],
            complemento=fornecedor_data["complemento"],
            cep=fornecedor_data["cep"],
            bairro=fornecedor_data["bairro"],
            uf=fornecedor_data["uf"],
            ddd=fornecedor_data["ddd"],
            natureza_juridica=fornecedor_data["natureza_juridica"],
            atividade_economica_principal=fornecedor_data["atividade_economica_principal"],
            atividade_economica_code=fornecedor_data["atividade_economica_code"]
        )

if __name__ == "__main__":
    # cnpj_ja_api_requester = CNPJJAAPIRequester(
    #     api_key="91c5ddae-60a6-4388-902c-340f290946e6-133f97d9-b8ae-44f9-ad86-3c1771cf4a8a",
    #     max_age=1,
    #     env="prod"
    # )
    # print(cnpj_ja_api_requester._base_url)
    # result = cnpj_ja_api_requester.get(CNPJ("64223915000149"))
    # print(result)
    rpc_response = rpc_call(queue='cnpj.rpc', body={'action': 'cnpj.consultation', 'cnpj': document}, timeout=600)





    

        
        

    