import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # Mock API response for transactions
        await page.route("**/api/v1/account/*/transactions", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"data": [{"from": "3an123", "to": "3an456", "amount": "1000000000", "block": 100, "timestamp": 1786171383594}]}'
        ))

        await page.goto('https://verdischain.com/wallet/', wait_until='networkidle')

        # Create wallet
        await page.click('.auth-card:first-child')
        await page.click('button:has-text("Generate New Wallet")')
        await page.wait_for_timeout(1000)

        # Click History tab
        await page.click('button.tab-btn:has-text("History")')
        await page.wait_for_timeout(1000)

        tx_html = await page.evaluate("document.getElementById('txHistory').innerHTML")
        print("txHistory HTML:", tx_html)
        print("Page errors:", page_errors)

        await browser.close()

asyncio.run(run())
