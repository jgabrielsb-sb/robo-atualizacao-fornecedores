from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
from botasaurus.lang import Lang

URL = "https://consopt.www8.receita.fazenda.gov.br/consultaoptantes"
ARGUMENTS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-blink-features=AutomationControlled",
]


@browser(
    user_agent=UserAgent.HASHED,
    lang=Lang.English,
    add_arguments=ARGUMENTS,
    output=None,
    wait_for_complete_page_load=True,
)
def scrape_opt_simples(
    driver: Driver,
    cnpj: str,
):
    driver.get(URL)
    driver.type("#Cnpj", cnpj)
    driver.click("button.h-captcha")
    driver.long_random_sleep()

    html = driver.page_html
    return html


def is_optante_simples(cnpj: str, html: str) -> bool | None:
    STR_OPTANTE_SIMPLES = "Optante pelo Simples Nacional"
    STR_NAO_OPTANTE_SIMPLES = "NÃO optante pelo Simples Nacional"
    STR_CNPJ_INVALIDO = "CNPJ inválido"

    if STR_NAO_OPTANTE_SIMPLES in html:
        return False
    if STR_OPTANTE_SIMPLES in html:
        return True
    if STR_CNPJ_INVALIDO in html:
        raise ValueError(f"CNPJ inválido: {cnpj}")
    return None


def get_opt_simples(cnpj: str) -> bool | None:
    html = scrape_opt_simples(cnpj)
    return is_optante_simples(cnpj, html)
