import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        console_logs = []
        page_errors = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        await page.goto('https://verdischain.com/wallet/', wait_until='networkidle')

        # Create wallet
        await page.click('.auth-card:first-child')
        await page.click('button:has-text("Generate New Wallet")')
        await page.wait_for_timeout(1000)

        # Fill send form
        await page.fill('#sendTo', '3anVSL4xaXTwLzPTC9MeFH6R2oVh2T3qfrXrFvkhiiRNVozGQFw')
        await page.fill('#sendAmount', '5')
        await page.fill('#sendMemo', 'Test memo')

        # Click send button
        print("Clicking Send Transaction...")
        await page.click('#sendBtn')
        await page.wait_for_timeout(2000)

        print("Console logs during send:")
        for l in console_logs:
            print("  ", l)

        print("Page errors during send:")
        for e in page_errors:
            print("  ", e)

        # Check toast message or UI state
        toast_text = await page.evaluate("""() => {
            const toasts = document.querySelectorAll('.toast');
            return Array.from(toasts).map(t => t.textContent);
        }""")
        print("Toasts displayed:", toast_text)

        await browser.close()

asyncio.run(run())
