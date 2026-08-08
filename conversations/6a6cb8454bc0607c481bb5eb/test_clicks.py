import asyncio
from playwright.async_api import async_playwright

async def test_dom_clicks():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        console_logs = []
        page_errors = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        await page.goto('https://verdischain.com/wallet/', wait_until='networkidle')

        # Create wallet
        await page.click('.auth-card:first-child')
        await page.wait_for_timeout(200)
        await page.click('button:has-text("Generate New Wallet")')
        await page.wait_for_timeout(1000)

        # Test Receive button on address card
        print("Clicking Receive button on address card...")
        await page.click('button:has-text("Receive")')
        await page.wait_for_timeout(500)
        await page.screenshot(path="screenshot_receive_tab.png")

        # Test History tab click
        print("Clicking History tab...")
        await page.click('button.tab-btn:has-text("History")')
        await page.wait_for_timeout(500)
        await page.screenshot(path="screenshot_history_tab.png")

        # Test Stake tab click
        print("Clicking Stake tab...")
        await page.click('button.tab-btn:has-text("Stake")')
        await page.wait_for_timeout(500)
        await page.screenshot(path="screenshot_stake_tab.png")

        print("\n=== CONSOLE LOGS ===")
        for l in console_logs:
            print("  ", l)

        print("\n=== PAGE ERRORS ===")
        for e in page_errors:
            print("  ", e)

        await browser.close()

asyncio.run(test_dom_clicks())
