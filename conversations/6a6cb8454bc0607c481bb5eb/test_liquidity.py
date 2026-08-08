import asyncio
from playwright.async_api import async_playwright

async def test_liq():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto('https://verdischain.com/dex/')
        await page.wait_for_timeout(2000)

        # Switch to liquidity tab
        await page.click('#tabBtn-liquidity')
        await page.wait_for_timeout(500)

        # Check content of liquidity tab
        html_liq = await page.inner_html('#pane-liquidity')
        print("=== LIQUIDITY TAB HTML ===")
        print(html_liq[:1500])

        # Test pair select dropdown
        pair_select = await page.query_selector('#addPairSelect')
        if pair_select:
            options = await pair_select.query_selector_all('option')
            print(f"\nAdd Pair Select options count: {len(options)}")
            for opt in options:
                print(" Option:", await opt.inner_text(), "Value:", await opt.get_attribute('value'))

        # Test typing in Add Liquidity input
        input_a = await page.query_selector('#addAmountA')
        if input_a:
            await input_a.fill('1000')
            await page.wait_for_timeout(300)
            input_b_val = await page.input_value('#addAmountB')
            lp_tokens = await page.inner_text('#addLpTokens')
            print(f"\nAdd Liquidity: Input 1000 A -> Input B: {input_b_val}, LP Tokens Minted: {lp_tokens}")

        # Test Add Liquidity Button
        dialog_messages = []
        page.on("dialog", lambda dialog: (dialog_messages.append(dialog.message), asyncio.create_task(dialog.accept())))

        add_btn = await page.query_selector("button:has-text('Add Liquidity')")
        if add_btn:
            await add_btn.click()
            await page.wait_for_timeout(500)
            print("Add Liquidity Dialog:", dialog_messages)

        # Test Remove Liquidity section
        print("\n=== REMOVE LIQUIDITY ===")
        slider = await page.query_selector('#removeSlider')
        if slider:
            # Change slider value
            await slider.fill('75')
            await page.evaluate("document.getElementById('removeSlider').dispatchEvent(new Event('input'))")
            await page.wait_for_timeout(300)

            pct_text = await page.inner_text('#removePctText')
            rec_a = await page.inner_text('#removeReceiveA')
            rec_b = await page.inner_text('#removeReceiveB')
            print(f"Slider 75% -> Text: {pct_text}, Receive A: {rec_a}, Receive B: {rec_b}")

        remove_btn = await page.query_selector("button:has-text('Remove Liquidity')")
        if remove_btn:
            await remove_btn.click()
            await page.wait_for_timeout(500)
            print("Remove Liquidity Dialog:", dialog_messages)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_liq())
