import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        await page.goto('https://verdischain.com/wallet/', wait_until='networkidle')

        # Create wallet
        await page.click('.auth-card:first-child')
        await page.click('button:has-text("Generate New Wallet")')
        await page.wait_for_timeout(1000)

        # Check Receive button
        await page.click('button:has-text("Receive")')
        await page.wait_for_timeout(300)

        tab_state_receive = await page.evaluate("""() => {
            return {
                receiveTabActive: document.getElementById('tab-receive').classList.contains('active'),
                receiveBtnActive: Array.from(document.querySelectorAll('.tab-btn'))[1].classList.contains('active'),
                qrContent: document.getElementById('qrCode').innerHTML.slice(0, 100),
                receiveAddressText: document.getElementById('receiveAddress').textContent
            }
        }""")
        print("Receive Tab State:", tab_state_receive)

        # Check History tab
        await page.click('button.tab-btn:has-text("History")')
        await page.wait_for_timeout(1000)

        history_state = await page.evaluate("""() => {
            return {
                historyTabActive: document.getElementById('tab-history').classList.contains('active'),
                txHistoryHTML: document.getElementById('txHistory').innerHTML
            }
        }""")
        print("History Tab State:", history_state)

        # Check Stake tab
        await page.click('button.tab-btn:has-text("Stake")')
        await page.wait_for_timeout(1000)

        stake_state = await page.evaluate("""() => {
            return {
                stakeTabActive: document.getElementById('tab-stake').classList.contains('active'),
                validatorListHTML: document.getElementById('validatorList').innerHTML
            }
        }""")
        print("Stake Tab State:", stake_state)

        print("\nPage errors:", page_errors)

        await browser.close()

asyncio.run(run())
