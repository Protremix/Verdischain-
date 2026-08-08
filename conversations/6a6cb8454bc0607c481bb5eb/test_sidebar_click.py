import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        page_errors = []
        console_logs = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on("console", lambda m: console_logs.append(f"[{m.type}] {m.text}"))

        await page.goto('https://verdischain.com/api/docs/?nocache=50025', wait_until='networkidle')

        # Click on sidebar group title "STATE"
        state_title = await page.query_selector('.sidebar-group-title')
        if state_title:
            print("Clicking sidebar group title:", await state_title.inner_text())
            await state_title.click()
            await page.wait_for_timeout(500)

        print("Page Errors after click:")
        for e in page_errors:
            print("  ", e)

        print("Console Logs:")
        for c in console_logs:
            print("  ", c)

        await browser.close()

asyncio.run(run())
