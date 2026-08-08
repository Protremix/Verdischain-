import asyncio
from playwright.async_api import async_playwright

async def trace_error():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Listen to pageerror with detail
        page.on("pageerror", lambda err: print(f"Page Error: {err}\nStack: {err.stack if hasattr(err, 'stack') else 'No stack'}"))

        # We can inject JS before script execution or hook into console
        await page.goto('https://verdischain.com/dex/')
        await page.wait_for_timeout(2000)

        # Let's evaluate which element IDs are missing
        ids_checked = await page.evaluate('''() => {
            const missing = [];
            const idsNeeded = [
                'rpcStatusText', 'rpcDot', 'amountIn', 'amountOut', 
                'symbolIn', 'symbolOut', 'balanceIn', 'balanceOut',
                'activePoolPair', 'swapRate', 'priceImpact', 'minReceived',
                'lpFee', 'resAVal', 'resBVal', 'slipValDisplay',
                'poolsTableBody', 'topPoolsList', 'addPairSelect',
                'addSymbolA', 'addSymbolB', 'addAmountA', 'addAmountB',
                'addLpTokens', 'removeSlider', 'removePctText',
                'removeReceiveA', 'removeReceiveB', 'priceChart',
                'historyTableBody', 'walletBtn', 'tokenList', 'tokenModal'
            ];
            for (const id of idsNeeded) {
                if (!document.getElementById(id)) {
                    missing.push(id);
                }
            }
            return missing;
        }''')

        print("=== MISSING DOM ELEMENT IDs ===")
        print(ids_checked)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(trace_error())
