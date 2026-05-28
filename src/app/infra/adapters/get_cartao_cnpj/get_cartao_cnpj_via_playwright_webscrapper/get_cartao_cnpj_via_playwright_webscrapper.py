import asyncio
import logging

from playwright.async_api import Page

from app.infra.adapters.get_cartao_cnpj.get_cartao_cnpj_via_playwright_webscrapper.locator import CnpjConsultationLocation
from app.infra.webscrapping.utils.captcha import resolve_captcha, verify_captcha_resolved

logger = logging.getLogger('rabbitmq')


class GetCartaoCNPJViaPlaywrightWebscrapper:
    """Encapsulates interactions with the Receita Federal CNPJ consultation form."""

    def __init__(self, page: Page) -> None:
        self.page = page

    async def navigate(self) -> None:
        """Navigate to the consultation page and wait for hCaptcha to load."""
        url = CnpjConsultationLocation.BASE_URL
        await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        selector = CnpjConsultationLocation.HCAPTCHA_IFRAME
        await self.page.wait_for_selector(selector, timeout=30000)
        await asyncio.sleep(2)

    async def fill_cnpj(self, cnpj: str) -> None:
        """Fill in the CNPJ field."""
        await self.page.locator(
            "xpath=//label[contains(text(), 'CNPJ:')]/parent::div/div/input"
        ).fill(cnpj)
        
    async def resolve_captcha(self) -> bool:
        """Resolve hCaptcha. Returns True if resolved successfully."""
        logger.info("Resolving hCaptcha...")
        agent = await resolve_captcha(self.page)

        if not agent.cr_list:
            logger.error("Failed to resolve hCaptcha.")
            return False

        cr = agent.cr_list[-1]
        logger.info(f"hCaptcha resolved! pass={cr.is_pass}")

        await verify_captcha_resolved(self.page)
        await asyncio.sleep(2)
        return True

    async def submit(self) -> None:
        """Submit the consultation form."""
        logger.info("Submitting form...")
        selector = CnpjConsultationLocation.SUBMIT_BUTTON
        await self.page.locator(
            "xpath=//button[contains(text(), 'Consultar')]"
        ).click()
        
        await self.page.wait_for_load_state("domcontentloaded", timeout=60000)
