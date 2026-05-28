import asyncio
from playwright_stealth import Stealth
from playwright.async_api import async_playwright

import time
async def main():
    async with Stealth().use_async(async_playwright()) as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://web-scraping.dev/products")
        title = await page.title()
        print(f"Page title: {title}")
        products = await page.evaluate("""
            Array.from(document.querySelectorAll('.product')).slice(0, 5).map(item => ({
                title: item.querySelector('h3 a')?.textContent?.trim(),
                price: item.querySelector('.price')?.textContent?.trim()
            }))
        """)
        for product in products:
            print(f"{product['title']}: {product['price']}")
        time.sleep(100000000)
        await browser.close()

asyncio.run(main())