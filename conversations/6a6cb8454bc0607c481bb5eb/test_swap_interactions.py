import asyncio
from playwright.async_api import async_playwright

async def test_swap():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ['error', 'warning'] else None)
        page.on("pageerror", lambda err: console_errors.append(f"[Uncaught Error] {err}"))

        await page.goto('https://verdischain.com/dex/')
        await page.wait_for_timeout(2000)

        print("--- Testing Amount Input ---")
        await page.fill('#amountIn', '500')
        await page.wait_for_timeout(500)

        out_val = await page.input_value('#amountOut')
        rate = await page.inner_text('#swapRate')
        impact = await page.inner_text('#priceImpact')
        min_rec = await page.inner_text('#minReceived')
        lp_fee = await page.inner_text('#lpFee')

        print(f"Input: 500 VRDX -> Output: {out_val}")
        print(f"Rate: {rate}")
        print(f"Impact: {impact}")
        print(f"Min Received: {min_rec}")
        print(f"LP Fee: {lp_fee}")

        print("\n--- Testing Slippage Buttons ---")
        slip_btns = await page.query_selector_all('.slip-btn')
        for i, btn in enumerate(slip_btns):
            txt = await btn.inner_text()
            print(f"Clicking slippage button {txt}...")
            try:
                await btn.click()
                await page.wait_for_timeout(200)
            except Exception as e:
                print(f"Error clicking slippage button: {e}")

        print("\n--- Testing Token Modal Selector ---")
        token_btn_in = await page.query_selector('.token-select-btn')
        await token_btn_in.click()
        await page.wait_for_timeout(500)
        
        modal_visible = await page.is_visible('#tokenModal')
        print(f"Token Modal Visible: {modal_visible}")
        if modal_visible:
            token_items = await page.query_selector_all('.token-item')
            print(f"Token list items count: {len(token_items)}")
            if len(token_items) > 2:
                # Select CARBON
                await token_items[2].click()
                await page.wait_for_timeout(500)
                print("Selected CARBON token.")

        print("\n--- Testing Invert Swap (Flip) ---")
        invert_btn = await page.query_selector('.swap-arrow-btn')
        await invert_btn.click()
        await page.wait_for_timeout(500)
        symbol_in = await page.inner_text('#symbolIn')
        symbol_out = await page.inner_text('#symbolOut')
        print(f"After invert: In={symbol_in}, Out={symbol_out}")

        print("\n--- Testing Swap Execution Button ---")
        # Handle dialog alert
        dialog_messages = []
        page.on("dialog", lambda dialog: (dialog_messages.append(dialog.message), asyncio.create_task(dialog.accept())))

        swap_btn = await page.query_selector('#swapSubmitBtn')
        await swap_btn.click()
        await page.wait_for_timeout(1000)
        print("Dialog messages received:", dialog_messages)

        print("\n--- Console / Uncaught Errors ---")
        for err in console_errors:
            print(err)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_swap())
