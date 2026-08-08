import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Intercept API call to return a transaction list
        await page.route("**/api/v1/account/*/transactions", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='[{"from": "3an123", "to": "3an456", "amount": "1000000000", "block": 100, "timestamp": 1786171383594}]'
        ))

        await page.goto('https://verdischain.com/wallet/', wait_until='networkidle')

        # Create wallet
        await page.click('.auth-card:first-child')
        await page.click('button:has-text("Generate New Wallet")')
        await page.wait_for_timeout(1000)

        # Inspect window errors
        err_message = await page.evaluate("""async () => {
            const wallet = JSON.parse(localStorage.getItem('verdis_wallet'));
            const res = await fetch('https://verdischain.com/api/v1/account/' + wallet.address + '/transactions');
            const txs = await res.json();
            try {
                txs.map(tx => {
                    const isIncoming = tx.to?.toLowerCase() === wallet.address.toLowerCase();
                    const otherAddr = isIncoming ? tx.from : tx.to;
                    return `<div class="tx-icon ${incoming ? 'in' : 'out'}">${isIncoming ? '↓' : '↑'}</div>`;
                });
                return "No Error";
            } catch(e) {
                return e.stack;
            }
        }""")

        print("Error evaluating template string in loadHistory:", err_message)

        await browser.close()

asyncio.run(run())
