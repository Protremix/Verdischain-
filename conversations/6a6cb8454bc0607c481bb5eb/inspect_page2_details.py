import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        console_logs = []
        page_errors = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        await page.goto('https://verdischain.com/api/docs/?nocache=50025', wait_until='networkidle')

        await page.screenshot(path='page2_desktop.png', full_page=True)

        # Check DOM stats
        stats = await page.evaluate('''() => {
            const h1 = document.querySelector('h1')?.innerText;
            const subtitle = document.querySelector('.hero p')?.innerText || document.querySelector('header p')?.innerText;
            const endpointCards = document.querySelectorAll('.endpoint-card, .ep-card, .card, [data-endpoint]').length;
            const sidebarItems = document.querySelectorAll('.sidebar a, .nav-item, li').length;
            const statsText = document.body.innerText;
            return {
                h1,
                subtitle,
                endpointCards,
                sidebarItems,
                bodyTextSnippet: statsText.substring(0, 1000)
            };
        }''')

        print("Page 2 DOM Stats:")
        print(json.dumps(stats, indent=2))

        print("\nConsole Logs:")
        for l in console_logs:
            print(l)

        print("\nPage Errors:")
        for e in page_errors:
            print(e)

        await browser.close()

asyncio.run(run())
