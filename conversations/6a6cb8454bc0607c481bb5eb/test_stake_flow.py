import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto('https://verdischain.com/wallet/', wait_until='networkidle')

        # Create wallet
        await page.click('.auth-card:first-child')
        await page.click('button:has-text("Generate New Wallet")')
        await page.wait_for_timeout(1000)

        # Click Stake tab
        await page.click('button.tab-btn:has-text("Stake")')
        await page.wait_for_timeout(1000)

        # Fill stake amount in first validator
        input_el = page.locator('.validator-item input').first
        await input_el.fill('10')

        # Click Stake button on first validator
        stake_btn = page.locator('.validator-item button').first
        await stake_btn.click()
        await page.wait_for_timeout(1000)

        toasts = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.toast')).map(t => t.textContent);
        }""")
        print("Toasts displayed during staking:", toasts)

        await browser.close()

asyncio.run(run())
