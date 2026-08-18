

class CnpjConsultationLocation:
    BASE_URL = (
        "https://solucoes.receita.fazenda.gov.br"
        "/servicos/cnpjreva/cnpjreva_solicitacao.asp"
    )
    
    CNPJ_INPUT = "#cnpj"
    SUBMIT_BUTTON = "button[type='submit']"
    HCAPTCHA_IFRAME = "iframe[src*='hcaptcha']"