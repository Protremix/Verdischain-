import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        await page.goto('https://verdischain.com/api/docs/?nocache=50025', wait_until='networkidle')

        # Find "Try It" button or try sending request
        try_btn = await page.query_selector('button:has-text("Execute"), button:has-text("Try"), button:has-text("Send"), button:has-text("Run")')
        print("Try button found:", bool(try_btn))
        if try_btn:
            print("Button text:", await try_btn.inner_text())

        # Inspect form / RPC endpoint inputs
        endpoint_info = await page.evaluate('''() => {
            const inputs = Array.from(document.querySelectorAll('input, select, textarea')).map(i => ({
                id: i.id,
                name: i.name,
                type: i.type,
                value: i.value,
                placeholder: i.placeholder
            }));
            const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText);
            return { inputs, buttons };
        }''')
        print("Page 2 Form Elements & Buttons:")
        print(json.dumps(endpoint_info, indent=2))

        await browser.close()

asyncio.run(run())
