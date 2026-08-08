import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        await page.goto('https://verdischain.com/dex/', wait_until='networkidle')
        await page.wait_for_timeout(2000)

        # Get body text
        text = await page.inner_text('body')
        print("=== BODY TEXT SAMPLE ===")
        print(text[:2000])
        print("========================")

        # Get all links, buttons, inputs, tabs
        buttons = await page.query_selector_all('button, a, input, select')
        print(f"\nFound {len(buttons)} interactive elements.")
        for i, b in enumerate(buttons[:30]):
            tag = await b.evaluate('el => el.tagName')
            txt = (await b.inner_text()).strip() if tag != 'INPUT' else await b.get_attribute('placeholder')
            id_attr = await b.get_attribute('id')
            class_attr = await b.get_attribute('class')
            print(f"[{i}] {tag} id='{id_attr}' class='{class_attr}' text/placeholder='{txt}'")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
