"""Browser manager that launches real Chrome and connects via CDP (async Playwright)."""

import asyncio
import shutil
import subprocess
import zipfile
from pathlib import Path

from playwright.async_api import Page, async_playwright

try:
    from playwright_stealth import Stealth
except ImportError:
    Stealth = None

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

_CDP_PORT = 9222

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
_PROFILE_DIR = _PROJECT_ROOT / "data" / "profiles" / "chrome_profile"
print(_PROFILE_DIR)

_stealth = (
    Stealth(
        navigator_platform_override="Linux x86_64",
        navigator_languages_override=("pt-BR", "pt"),
    )
    if Stealth
    else None
)


def _ensure_profile() -> Path:
    """Ensure Chrome profile is extracted and return the user_data_dir path."""
    if not _PROFILE_DIR.exists():
        raise FileNotFoundError(
            f"Chrome profile not found: {_PROFILE_DIR}\n"
        )
    return _PROFILE_DIR


def _find_chrome() -> str:
    """Find the Google Chrome executable on the system."""
    for name in ("google-chrome", "google-chrome-stable"):
        path = shutil.which(name)
        if path:
            return path
    raise FileNotFoundError("Google Chrome not found on the system")


class CdpBrowserManager:
    """Launches real Chrome and connects via CDP using async Playwright."""

    def __init__(self, headless: bool = False) -> None:
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._process = None
        self.context = None
        self.page: Page | None = None

    async def __aenter__(self) -> "CdpBrowserManager":
        user_data_dir = _ensure_profile()
        chrome_path = _find_chrome()

        args = [
            chrome_path,
            f"--remote-debugging-port={_CDP_PORT}",
            f"--user-data-dir={user_data_dir}",
        ]
        if self.headless:
            args.append("--headless=new")

        self._process = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        await asyncio.sleep(2)

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.connect_over_cdp(
            f"http://localhost:{_CDP_PORT}"
        )
        self.context = self._browser.contexts[0]
        self.page = await self.context.new_page()

        if _stealth:
            await _stealth.apply_stealth_async(self.page)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
        if self._process:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
    
