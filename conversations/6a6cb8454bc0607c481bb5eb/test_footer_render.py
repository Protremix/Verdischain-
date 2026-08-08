import asyncio
import os
from playwright.async_api import async_playwright

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/tmp/pw-browsers"

async def test_footer():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto("https://verdischain.com/wallet/?nocache=50004", wait_until="networkidle")
        
        footer_links = await page.eval_on_selector_all("footer.footer .footer-links a", """els => els.map(e => {
            let rect = e.getBoundingClientRect();
            let style = window.getComputedStyle(e);
            return {
                text: e.innerText,
                href: e.href,
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                marginRight: style.marginRight,
                paddingRight: style.paddingRight
            };
        })""")
        
        print("Footer links rendering details:")
        for fl in footer_links:
            print(fl)

        # Check visual appearance of footer
        await page.locator("footer.footer").screenshot(path="screenshot_footer.png")
        print("Saved screenshot_footer.png")

        await browser.close()

asyncio.run(test_footer())
