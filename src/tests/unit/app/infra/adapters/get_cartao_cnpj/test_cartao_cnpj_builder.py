import pytest

from app.infra.adapters.get_cartao_cnpj import CartaoCNPJBuilder

from app.application.ports import MunicipioLookupPort
from app.domain.enums import PorteEnum
from app.domain.value_objects import (
    CartaoCNPJ, 
    Telefone, 
    Municipio,
    CodigoMunicipioIBGE,
    DDD,
    Endereco,
    CEP,
)


element_data_1 = {
    "queue_response": {
      "status": "ok",
      "action": "cnpj.consultation",
      "cnpj": "21402456000158",
      "data": {
        "cnpj": "21.402.456/0001-58",
        "type": None,
        "opening_date": "13/11/2014",
        "legal_name": "21.402.456 DORACY MENDES SILVA DA ROCHA",
        "trade_name": None,
        "size": "ME",
        "primary_activity": {
          "code": "47.81-4-00",
          "description": "Comércio varejista de artigos do vestuário e acessórios"
        },
        "secondary_activities": [
          {
            "code": "47.55-5-03",
            "description": "Comercio varejista de artigos de cama, mesa e banho"
          },
          {
            "code": "47.72-5-00",
            "description": "Comércio varejista de cosméticos, produtos de perfumaria e de higiene pessoal"
          }
        ],
        "legal_nature": {
          "code": "213-5",
          "description": "Empresário (Individual)"
        },
        "address": {
          "street": "R SANTO ANTONIO",
          "number": "270",
          "complement": "QUADRA 53, LOTE 04",
          "zip_code": "78.643-000",
          "neighborhood": "SETOR NOVA QUERENCIA",
          "city": "QUERENCIA",
          "state": "MT"
        },
        "contact": {
          "email": "samara.91_forever@hotmail.com",
          "phone": "(66) 9651-6772"
        },
        "responsible_federative_entity": None,
        "registration_status": {
          "status": "ATIVA",
          "date": "13/11/2014",
          "reason": None
        },
        "special_status": {
          "status": None,
          "date": None
        }
      }
    },
    "expected_result": CartaoCNPJ(
      porte=PorteEnum.ME,
      razao_social="21.402.456 DORACY MENDES SILVA DA ROCHA",
      nome_fantasia=None,
      atividade_economica_principal_str="Comércio varejista de artigos do vestuário e acessórios",
      telefone=Telefone(ddd=DDD(value="66"), numero="96516772"),
      endereco=Endereco(
        endereco="R SANTO ANTONIO",
        numero="270",
        complemento="QUADRA 53, LOTE 04",
        cep=CEP(value="78643000"),
        municipio=Municipio(
          nome="QUERENCIA",
          codigo_ibge=CodigoMunicipioIBGE(value="123456"),
        ),
      ),
      natureza_juridica="Empresário (Individual)",
      situacao_cadastral="ATIVA",
    ),   
}

element_data_2 = {
    "queue_response": {
      "status": "ok",
      "action": "cnpj.consultation",
      "cnpj": "28738609000181",
      "data": {
        "cnpj": "28.738.609/0001-81",
        "type": None,
        "opening_date": "27/09/2017",
        "legal_name": "CLINICA CARDIOVIDA LTDA",
        "trade_name": "CARDIOVIDA",
        "size": "ME",
        "primary_activity": {
          "code": "86.30-5-02",
          "description": "Atividade médica ambulatorial com recursos para realização de exames complementares"
        },
        "secondary_activities": [
          {
            "code": "86.50-0-03",
            "description": "Atividades de psicologia e psicanálise"
          }
        ],
        "legal_nature": {
          "code": "206-2",
          "description": "Sociedade Empresária Limitada"
        },
        "address": {
          "street": "R BARAO DE ALAGOAS",
          "number": "118",
          "complement": None,
          "zip_code": "57.312-330",
          "neighborhood": "ALTO DO CRUZEIRO",
          "city": "ARAPIRACA",
          "state": "AL"
        },
        "contact": {
          "email": "INOVA@INOVAA.COM.BR",
          "phone": "(31) 9384-0004"
        },
        "responsible_federative_entity": None,
        "registration_status": {
          "status": "ATIVA",
          "date": "27/09/2017",
          "reason": None
        },
        "special_status": {
          "status": None,
          "date": None
        }
      }
    },
    "expected_result": CartaoCNPJ(
      porte=PorteEnum.ME,
      razao_social="CLINICA CARDIOVIDA LTDA",
      nome_fantasia="CARDIOVIDA",
      atividade_economica_principal_str="Atividade médica ambulatorial com recursos para realização de exames complementares",
      telefone=Telefone(ddd=DDD(value="31"), numero="93840004"),
      natureza_juridica="Sociedade Empresária Limitada",
      endereco=Endereco(
        endereco="R BARAO DE ALAGOAS",
        numero="118",
        complemento=None,
        cep=CEP(value="57312330"),
        municipio=Municipio(
          nome="ARAPIRACA",
          codigo_ibge=CodigoMunicipioIBGE(value="123457"),
        ),
      ),
      situacao_cadastral="ATIVA",
    ),
}

element_data_3 = {
    "queue_response": {
      "status": "ok",
      "action": "cnpj.consultation",
      "cnpj": "28738610000106",
      "data": {
        "cnpj": "28.738.610/0001-06",
        "type": None,
        "opening_date": "27/09/2017",
        "legal_name": "FREDSON NEVES DOS SANTOS 95721266520",
        "trade_name": None,
        "size": "ME",
        "primary_activity": {
          "code": None,
          "description": None
        },
        "secondary_activities": [],
        "legal_nature": {
          "code": "213-5",
          "description": "Empresário (Individual)"
        },
        "address": {
          "street": None,
          "number": None,
          "complement": None,
          "zip_code": None,
          "neighborhood": None,
          "city": None,
          "state": None
        },
        "contact": {
          "email": None,
          "phone": "(17) 3379-5312"
        },
        "responsible_federative_entity": None,
        "registration_status": {
          "status": "INAPTA",
          "date": "07/04/2021",
          "reason": "Omissão De Declarações"
        },
        "special_status": {
          "status": None,
          "date": None
        }
      }
    },
    "expected_result": CartaoCNPJ(
      porte=PorteEnum.ME,
      razao_social="FREDSON NEVES DOS SANTOS 95721266520",
      nome_fantasia=None,
      atividade_economica_principal_str=None,
      telefone=Telefone(ddd=DDD(value="17"), numero="33795312"),
      natureza_juridica="Empresário (Individual)",
      endereco=None,
      situacao_cadastral="INAPTA",
    ),
}

element_data_4 = {
    "queue_response": {
      "status": "ok",
      "action": "cnpj.consultation",
      "cnpj": "28738612000103",
      "data": {
        "cnpj": "28.738.612/0001-03",
        "type": None,
        "opening_date": "27/09/2017",
        "legal_name": "ROGERIO JANUARIO CARDOSO DA SILVA 00695175920",
        "trade_name": None,
        "size": "ME",
        "primary_activity": {
          "code": "43.30-4-05",
          "description": "Aplicação de revestimentos e de resinas em interiores e exteriores"
        },
        "secondary_activities": [
          {
            "code": "43.30-4-04",
            "description": "Serviços de pintura de edifícios em geral"
          },
          {
            "code": "43.22-3-01",
            "description": "Instalações hidráulicas, sanitárias e de gás"
          },
          {
            "code": "43.99-1-03",
            "description": "Obras de alvenaria"
          }
        ],
        "legal_nature": {
          "code": "213-5",
          "description": "Empresário (Individual)"
        },
        "address": {
          "street": "R CARLOS MAURICIO DUARTE",
          "number": "155",
          "complement": None,
          "zip_code": "87.053-751",
          "neighborhood": "RESIDENCIAL PIONEIRO ODWALDO BUENO NETTO",
          "city": "MARINGA",
          "state": "PR"
        },
        "contact": {
          "email": None,
          "phone": "(44) 9994-3915"
        },
        "responsible_federative_entity": None,
        "registration_status": {
          "status": "ATIVA",
          "date": "27/09/2017",
          "reason": None
        },
        "special_status": {
          "status": None,
          "date": None
        }
      }
    },
    "expected_result": CartaoCNPJ(
      porte=PorteEnum.ME,
      razao_social="ROGERIO JANUARIO CARDOSO DA SILVA 00695175920",
      nome_fantasia=None,
      atividade_economica_principal_str="Aplicação de revestimentos e de resinas em interiores e exteriores",
      telefone=Telefone(ddd=DDD(value="44"), numero="99943915"),
      natureza_juridica="Empresário (Individual)",
      endereco=Endereco(
        endereco="R CARLOS MAURICIO DUARTE",
        numero="155",
        complemento=None,
        cep=CEP(value="87053751"),
        municipio=Municipio(
          nome="MARINGA",
          codigo_ibge=CodigoMunicipioIBGE(value="123458"),
        ),
      ),
      situacao_cadastral="ATIVA",
    ),
}

element_data_5 = {
    "queue_response": {
      "status": "ok",
      "action": "cnpj.consultation",
      "cnpj": "16819228000148",
      "data": {
        "cnpj": "16.819.228/0001-48",
        "type": None,
        "opening_date": "10/09/2012",
        "legal_name": "MANDALA PROMOCAO E MARKETING LTDA",
        "trade_name": None,
        "size": "DEMAIS",
        "primary_activity": {
          "code": "82.30-0-01",
          "description": "Serviços de organização de feiras, congressos, exposições e festas"
        },
        "secondary_activities": [
          {
            "code": "68.10-2-02",
            "description": "Aluguel de imóveis próprios"
          },
          {
            "code": "73.11-4-00",
            "description": "Agências de publicidade"
          },
          {
            "code": "73.12-2-00",
            "description": "Agenciamento de espaços para publicidade, exceto em veículos de comunicação"
          },
          {
            "code": "73.19-0-02",
            "description": "Promoção de vendas"
          },
          {
            "code": "73.19-0-03",
            "description": "Marketing direto"
          }
        ],
        "legal_nature": {
          "code": "206-2",
          "description": "Sociedade Empresária Limitada"
        },
        "address": {
          "street": "AV COMENDADOR LEAO",
          "number": "958",
          "complement": None,
          "zip_code": "57.025-000",
          "neighborhood": "POCO",
          "city": "MACEIO",
          "state": "AL"
        },
        "contact": {
          "email": "manoel@mandalapromocoes.com.br",
          "phone": "(82) 3035-7163/ (82) 9351-0222"
        },
        "responsible_federative_entity": None,
        "registration_status": {
          "status": "ATIVA",
          "date": "10/09/2012",
          "reason": None
        },
        "special_status": {
          "status": None,
          "date": None
        }
      }
    },
    "expected_result": CartaoCNPJ(
      porte=PorteEnum.D,
      razao_social="MANDALA PROMOCAO E MARKETING LTDA",
      nome_fantasia=None,
      atividade_economica_principal_str="Serviços de organização de feiras, congressos, exposições e festas",
      telefone=Telefone(ddd=DDD(value="82"), numero="30357163"),
      natureza_juridica="Sociedade Empresária Limitada",
      endereco=Endereco(
        endereco="AV COMENDADOR LEAO",
        numero="958",
        complemento=None,
        cep=CEP(value="57025000"),
        municipio=Municipio(
          nome="MACEIO",
          codigo_ibge=CodigoMunicipioIBGE(value="123459"),
        ),
      ),
      situacao_cadastral="ATIVA",
    ),
}

DATA = [element_data_1, element_data_2, element_data_3, element_data_4, element_data_5]

@pytest.fixture
def fake_municipio_lookup_port():
    class FakeMunicipioLookupPort(MunicipioLookupPort):
        def get(self, municipio_name: str) -> Municipio:
            
            if municipio_name == "QUERENCIA":
              codigo_ibge = "123456"
            elif municipio_name == "ARAPIRACA":
              codigo_ibge = "123457"
            elif municipio_name == "MARINGA":
              codigo_ibge = "123458"
            elif municipio_name == "MACEIO":
              codigo_ibge = "123459"
            else:
              raise ValueError(f"Municipio {municipio_name} not found")

            return Municipio(
                nome=municipio_name,
                codigo_ibge=CodigoMunicipioIBGE(value=codigo_ibge),
            )

    return FakeMunicipioLookupPort()

@pytest.fixture
def cartao_cnpj_builder(fake_municipio_lookup_port):
    return CartaoCNPJBuilder(
        municipio_lookup_port=fake_municipio_lookup_port,
    )

@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_porte(
    data,
    cartao_cnpj_builder: CartaoCNPJBuilder,
):
  result = cartao_cnpj_builder.build(data["queue_response"])
  assert result.porte == data["expected_result"].porte

@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_razao_social(
    data,
    cartao_cnpj_builder: CartaoCNPJBuilder,
):
  result = cartao_cnpj_builder.build(data["queue_response"])
  assert result.razao_social == data["expected_result"].razao_social

@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_nome_fantasia(
    data,
    cartao_cnpj_builder: CartaoCNPJBuilder,
):
  result = cartao_cnpj_builder.build(data["queue_response"])
  assert result.nome_fantasia == data["expected_result"].nome_fantasia

@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_atividade_economica_principal_str(
    data,
    cartao_cnpj_builder: CartaoCNPJBuilder,
):
  result = cartao_cnpj_builder.build(data["queue_response"])
  assert result.atividade_economica_principal_str == data["expected_result"].atividade_economica_principal_str

@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_endereco(
    data,
    cartao_cnpj_builder: CartaoCNPJBuilder,
):
  result = cartao_cnpj_builder.build(data["queue_response"])
  assert result.endereco == data["expected_result"].endereco

@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_natureza_juridica(
    data,
    cartao_cnpj_builder: CartaoCNPJBuilder,
):
  result = cartao_cnpj_builder.build(data["queue_response"])
  assert result.natureza_juridica == data["expected_result"].natureza_juridica

@pytest.mark.parametrize("data", DATA)
def test_map_response_to_cartao_cnpj_returns_correct_situacao_cadastral(
    data,
    cartao_cnpj_builder: CartaoCNPJBuilder,
):
  result = cartao_cnpj_builder.build(data["queue_response"])
  assert result.situacao_cadastral == data["expected_result"].situacao_cadastral
  
