import pytest

from app.application.ports import MunicipioLookupPort
from app.domain.enums import PorteEnum, SituacaoCadastralEnum
from app.domain.value_objects import (
    CartaoCNPJ,
    CEP,
    CodigoMunicipioIBGE,
    DDD,
    Endereco,
    Municipio,
    Telefone,
)
from app.infra.adapters.get_cartao_cnpj import CartaoCNPJBuilder

# ---------------------------------------------------------------------------
# Raw queue responses paired with their expected CartaoCNPJ domain objects.
# Both the builder tests and the adapter tests mock at different layers but
# use the same response shapes, so the data lives here.
# ---------------------------------------------------------------------------

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
                "description": "Comércio varejista de artigos do vestuário e acessórios",
            },
            "secondary_activities": [
                {
                    "code": "47.55-5-03",
                    "description": "Comercio varejista de artigos de cama, mesa e banho",
                },
                {
                    "code": "47.72-5-00",
                    "description": "Comércio varejista de cosméticos, produtos de perfumaria e de higiene pessoal",
                },
            ],
            "legal_nature": {"code": "213-5", "description": "Empresário (Individual)"},
            "address": {
                "street": "R SANTO ANTONIO",
                "number": "270",
                "complement": "QUADRA 53, LOTE 04",
                "zip_code": "78.643-000",
                "neighborhood": "SETOR NOVA QUERENCIA",
                "city": "QUERENCIA",
                "state": "MT",
            },
            "contact": {
                "email": "samara.91_forever@hotmail.com",
                "phone": "(66) 9651-6772",
            },
            "responsible_federative_entity": None,
            "registration_status": {
                "status": "ATIVA",
                "date": "13/11/2014",
                "reason": None,
            },
            "special_status": {"status": None, "date": None},
        },
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
            bairro="SETOR NOVA QUERENCIA",
        ),
        natureza_juridica="Empresário (Individual)",
        situacao_cadastral=SituacaoCadastralEnum.ATIVA,
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
                "description": "Atividade médica ambulatorial com recursos para realização de exames complementares",
            },
            "secondary_activities": [
                {
                    "code": "86.50-0-03",
                    "description": "Atividades de psicologia e psicanálise",
                }
            ],
            "legal_nature": {
                "code": "206-2",
                "description": "Sociedade Empresária Limitada",
            },
            "address": {
                "street": "R BARAO DE ALAGOAS",
                "number": "118",
                "complement": None,
                "zip_code": "57.312-330",
                "neighborhood": "ALTO DO CRUZEIRO",
                "city": "ARAPIRACA",
                "state": "AL",
            },
            "contact": {
                "email": "INOVA@INOVAA.COM.BR",
                "phone": "(31) 9384-0004",
            },
            "responsible_federative_entity": None,
            "registration_status": {
                "status": "ATIVA",
                "date": "27/09/2017",
                "reason": None,
            },
            "special_status": {"status": None, "date": None},
        },
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
            bairro="ALTO DO CRUZEIRO",
        ),
        situacao_cadastral=SituacaoCadastralEnum.ATIVA,
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
            "primary_activity": {"code": None, "description": None},
            "secondary_activities": [],
            "legal_nature": {
                "code": "213-5",
                "description": "Empresário (Individual)",
            },
            "address": {
                "street": None,
                "number": None,
                "complement": None,
                "zip_code": None,
                "neighborhood": None,
                "city": None,
                "state": None,
            },
            "contact": {"email": None, "phone": "(17) 3379-5312"},
            "responsible_federative_entity": None,
            "registration_status": {
                "status": "INAPTA",
                "date": "07/04/2021",
                "reason": "Omissão De Declarações",
            },
            "special_status": {"status": None, "date": None},
        },
    },
    "expected_result": CartaoCNPJ(
        porte=PorteEnum.ME,
        razao_social="FREDSON NEVES DOS SANTOS 95721266520",
        nome_fantasia=None,
        atividade_economica_principal_str=None,
        telefone=Telefone(ddd=DDD(value="17"), numero="33795312"),
        natureza_juridica="Empresário (Individual)",
        endereco=Endereco(
            endereco=None,
            numero=None,
            complemento=None,
            cep=None,
            municipio=None,
            bairro=None,
        ),
        situacao_cadastral=SituacaoCadastralEnum.INAPTA,
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
                "description": "Aplicação de revestimentos e de resinas em interiores e exteriores",
            },
            "secondary_activities": [
                {
                    "code": "43.30-4-04",
                    "description": "Serviços de pintura de edifícios em geral",
                },
                {
                    "code": "43.22-3-01",
                    "description": "Instalações hidráulicas, sanitárias e de gás",
                },
                {"code": "43.99-1-03", "description": "Obras de alvenaria"},
            ],
            "legal_nature": {
                "code": "213-5",
                "description": "Empresário (Individual)",
            },
            "address": {
                "street": "R CARLOS MAURICIO DUARTE",
                "number": "155",
                "complement": None,
                "zip_code": "87.053-751",
                "neighborhood": "RESIDENCIAL PIONEIRO ODWALDO BUENO NETTO",
                "city": "MARINGA",
                "state": "PR",
            },
            "contact": {"email": None, "phone": "(44) 9994-3915"},
            "responsible_federative_entity": None,
            "registration_status": {
                "status": "ATIVA",
                "date": "27/09/2017",
                "reason": None,
            },
            "special_status": {"status": None, "date": None},
        },
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
            bairro="RESIDENCIAL PIONEIRO ODWALDO BUENO NETTO",
        ),
        situacao_cadastral=SituacaoCadastralEnum.ATIVA,
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
                "description": "Serviços de organização de feiras, congressos, exposições e festas",
            },
            "secondary_activities": [
                {
                    "code": "68.10-2-02",
                    "description": "Aluguel de imóveis próprios",
                },
                {"code": "73.11-4-00", "description": "Agências de publicidade"},
                {
                    "code": "73.12-2-00",
                    "description": "Agenciamento de espaços para publicidade, exceto em veículos de comunicação",
                },
                {"code": "73.19-0-02", "description": "Promoção de vendas"},
                {"code": "73.19-0-03", "description": "Marketing direto"},
            ],
            "legal_nature": {
                "code": "206-2",
                "description": "Sociedade Empresária Limitada",
            },
            "address": {
                "street": "AV COMENDADOR LEAO",
                "number": "958",
                "complement": None,
                "zip_code": "57.025-000",
                "neighborhood": "POCO",
                "city": "MACEIO",
                "state": "AL",
            },
            "contact": {
                "email": "manoel@mandalapromocoes.com.br",
                "phone": "(82) 3035-7163/ (82) 9351-0222",
            },
            "responsible_federative_entity": None,
            "registration_status": {
                "status": "ATIVA",
                "date": "10/09/2012",
                "reason": None,
            },
            "special_status": {"status": None, "date": None},
        },
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
            bairro="POCO",
        ),
        situacao_cadastral=SituacaoCadastralEnum.ATIVA,
    ),
}

element_data_6 = {
    "queue_response": {
        "status": "ok",
        "action": "cnpj.consultation",
        "cnpj": "02356937000120",
        "data": {
            "uuid": "2b8a65dd-1883-4383-b068-194c0149dce6",
            "cnpj": "02356937000120",
            "legal_name": "MEDEIROS ENGENHARIA E ARQUITETURA LTDA",
            "trade_name": "ENGENHARQ",
            "type": "",
            "size": "ME",
            "opening_date": "1998-01-30",
            "registration_status": "ACTIVE",
            "registration_status_date": "2005-11-03",
            "registration_status_reason": "",
            "processing_status": "COMPLETED",
            "processing_error": "",
            "created_at": "2026-05-18T11:38:18.713544-03:00",
            "updated_at": "2026-05-18T11:38:51.390845-03:00",
            "legal_nature": {
            "code": "2062",
            "description": "Sociedade Empresária Limitada"
            },
            "address": {
            "street": "av joao davino",
            "number": "691",
            "complement": "a",
            "zip_code": "57035554",
            "neighborhood": "jatiuca",
            "city": "maceio",
            "state": "al"
            },
            "has_pending_declaration": False,
            "contacts": [
            {
                "type": "PHONE",
                "value": "8233251183"
            }
            ],
            "company_activities": [
            {
                "code": "7112000",
                "description": "Serviços de engenharia",
                "type": "PRIMARY"
            }
            ],
            "ratification_declarations": [],
            "has_overdue_boleto": False,
            "das_payments": [],
            "simples_nacional_status": "",
            "simei_status": "",
            "future_events_simples": "",
            "future_events_simei": "",
            "mei_trucker": "",
            "tax_regime_periods": [],
            "mei_registration_status": "",
            "mei_registration_detail": ""
        },
        "cached": True
        },
    "expected_result": CartaoCNPJ(
        porte=PorteEnum.ME,
        razao_social="MEDEIROS ENGENHARIA E ARQUITETURA LTDA",
        nome_fantasia="ENGENHARQ",
        atividade_economica_principal_str="Serviços de engenharia",
        telefone=Telefone(ddd=DDD(value="82"), numero="33251183"),
        natureza_juridica="Sociedade Empresária Limitada",
        endereco=Endereco(
            endereco="av joao davino",
            numero="691",
            complemento="a",
            cep=CEP(value="57035554"),
            municipio=Municipio(
                nome="MACEIO",
                codigo_ibge=CodigoMunicipioIBGE(value="123459"),
            ),
            bairro="jatiuca",
        ),
        situacao_cadastral=SituacaoCadastralEnum.ATIVA,
    ),
}


DATA = [element_data_1, element_data_2, element_data_3, element_data_4, element_data_5, element_data_6]

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_municipio_lookup_port():
    class FakeMunicipioLookupPort(MunicipioLookupPort):
        _municipio_map = {
            "QUERENCIA": "123456",
            "ARAPIRACA": "123457",
            "MARINGA":   "123458",
            "MACEIO":    "123459",
        }

        def get(self, municipio_name: str) -> Municipio:
            codigo_ibge = self._municipio_map.get(municipio_name)
            if not codigo_ibge:
                raise ValueError(f"Municipio {municipio_name} not found")
            return Municipio(
                nome=municipio_name,
                codigo_ibge=CodigoMunicipioIBGE(value=codigo_ibge),
            )

    return FakeMunicipioLookupPort()


@pytest.fixture
def cartao_cnpj_builder(fake_municipio_lookup_port):
    return CartaoCNPJBuilder(municipio_lookup_port=fake_municipio_lookup_port)
