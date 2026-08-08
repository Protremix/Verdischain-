import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        await page.goto('https://verdischain.com/api/docs/?nocache=50025', wait_until='networkidle')

        # Click Send Request for chain_getBlock
        await page.click('button:has-text("Send Request")')
        await page.wait_for_timeout(2000)

        response_box = await page.evaluate('''() => {
            const respEl = document.querySelector('#response, .response, pre code, #jsonResponse, #responseOutput');
            const codeBlocks = Array.from(document.querySelectorAll('pre')).map(p => p.innerText);
            return {
                codeBlocks
            };
        }''')

        print("Response Output after clicking Send Request:")
        print(json.dumps(response_box, indent=2))

        await browser.close()

asyncio.run(run())
