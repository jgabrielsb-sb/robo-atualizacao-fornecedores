from botasaurus.browser import browser, Driver
from botasaurus.user_agent import UserAgent
from botasaurus.lang import Lang

import time

URL = "https://consopt.www8.receita.fazenda.gov.br/consultaoptantes"
ARGUMENTS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-blink-features=AutomationControlled",
]


class GetOptSimplesError(Exception):
    pass


class CNPJInvalidoError(GetOptSimplesError):
    pass


class ResultadoNaoEncontradoError(GetOptSimplesError):
    pass


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
    time.sleep(5)
    driver.type("#Cnpj", cnpj)
    driver.click("button.h-captcha")
    driver.long_random_sleep()

    html = driver.page_html
    return html


def is_optante_simples(cnpj: str, html: str) -> bool:
    STR_OPTANTE_SIMPLES = "Optante pelo Simples Nacional"
    STR_NAO_OPTANTE_SIMPLES = "NÃO optante pelo Simples Nacional"
    # O input #Cnpj sempre carrega data-val-length="CNPJ inválido." como
    # atributo; só consideramos inválido quando a mensagem aparece como
    # texto renderizado (ex.: <span class="field-validation-error">CNPJ inválido.</span>)
    STR_CNPJ_INVALIDO = ">CNPJ inválido"

    if STR_NAO_OPTANTE_SIMPLES in html:
        return False
    if STR_OPTANTE_SIMPLES in html:
        return True
    if STR_CNPJ_INVALIDO in html:
        raise CNPJInvalidoError(f"CNPJ inválido: {cnpj}")
    # Nenhum resultado na página: provavelmente o hCaptcha não foi resolvido
    # ou a consulta foi bloqueada pela Receita.
    raise ResultadoNaoEncontradoError(
        f"Resultado da consulta de opção pelo Simples Nacional não encontrado "
        f"na página para o CNPJ {cnpj} (captcha não resolvido ou consulta bloqueada?)"
    )


def get_opt_simples(cnpj: str) -> bool:
    html = scrape_opt_simples(cnpj)
    return is_optante_simples(cnpj, html)
