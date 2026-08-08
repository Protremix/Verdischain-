import asyncio
from playwright.async_api import async_playwright

async def run_js_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto("https://verdischain.com/sale/?nocache=50005", wait_until="networkidle")

        # 1. Initial values in Buy Section
        pay_amount = await page.input_value('#payAmount')
        recv_amount = await page.input_value('#receiveAmount')
        total_receive = await page.inner_text('#totalReceive')
        base_tokens = await page.inner_text('#baseTokens')
        bonus_tokens = await page.inner_text('#bonusTokens')
        total_cost = await page.inner_text('#totalCost')
        output_rate = await page.inner_text('#outputRate')

        print("=== INITIAL BUY SECTION VALUES ===")
        print(f"payAmount input: {pay_amount}")
        print(f"receiveAmount input: {recv_amount}") # Notice this is empty initially until input event!
        print(f"totalReceive text: {total_receive}")
        print(f"baseTokens text: {base_tokens}")
        print(f"bonusTokens text: {bonus_tokens}")
        print(f"totalCost text: {total_cost}")
        print(f"outputRate text: {output_rate}")

        # Trigger calculatePurchase() by typing 1000 into payAmount
        await page.fill('#payAmount', '1000')
        
        recv_amount_after = await page.input_value('#receiveAmount')
        total_receive_after = await page.inner_text('#totalReceive')
        base_tokens_after = await page.inner_text('#baseTokens')
        bonus_tokens_after = await page.inner_text('#bonusTokens')
        total_cost_after = await page.inner_text('#totalCost')
        output_rate_after = await page.inner_text('#outputRate')

        print("\n=== AFTER TYPING 1000 IN INPUT (calculatePurchase triggered) ===")
        print(f"receiveAmount input: {recv_amount_after}")
        print(f"totalReceive text: {total_receive_after}")
        print(f"baseTokens text: {base_tokens_after}")
        print(f"bonusTokens text: {bonus_tokens_after}")
        print(f"totalCost text: {total_cost_after}")
        print(f"outputRate text: {output_rate_after}")

        # Check FAQ toggle
        faq_item = await page.query_selector('.faq-item')
        is_open_before = await page.evaluate("el => el.classList.contains('open')", faq_item)
        await page.click('.faq-q')
        is_open_after = await page.evaluate("el => el.classList.contains('open')", faq_item)

        print("\n=== FAQ TOGGLE TEST ===")
        print(f"Open before click: {is_open_before}, Open after click: {is_open_after}")

        await browser.close()

asyncio.run(run_js_tests())
