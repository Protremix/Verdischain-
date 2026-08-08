import asyncio
from playwright.async_api import async_playwright

async def test_liq():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto('https://verdischain.com/dex/')
        await page.wait_for_timeout(2000)

        await page.click('#tabBtn-liquidity')
        await page.wait_for_timeout(500)

        dialog_messages = []
        page.on("dialog", lambda dialog: (dialog_messages.append(dialog.message), asyncio.create_task(dialog.accept())))

        # Click Supply Liquidity
        supply_btn = await page.query_selector("button:has-text('Supply Liquidity')")
        if supply_btn:
            await supply_btn.click()
            await page.wait_for_timeout(500)
            print("Supply Liquidity Dialog:", dialog_messages)

        # Click Remove Liquidity
        remove_btn = await page.query_selector("button:has-text('Remove Liquidity')")
        if remove_btn:
            await remove_btn.click()
            await page.wait_for_timeout(500)
            print("Remove Liquidity Dialog:", dialog_messages)

        # Let's check what happens when changing pair in addPairSelect
        await page.select_option('#addPairSelect', 'VRDX/CARBON')
        await page.wait_for_timeout(300)

        sym_a = await page.inner_text('#addSymbolA')
        sym_b = await page.inner_text('#addSymbolB')
        print(f"Selected VRDX/CARBON: Symbol A={sym_a}, Symbol B={sym_b}")

        # Now test remove pair select
        await page.select_option('#removePairSelect', 'VRDX/CARBON')
        await page.wait_for_timeout(300)
        # Note: removePairSelect has NO onchange listener attached!
        rec_a = await page.inner_text('#removeReceiveA')
        rec_b = await page.inner_text('#removeReceiveB')
        print(f"Selected VRDX/CARBON in Remove: Receive A={rec_a}, Receive B={rec_b}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_liq())
