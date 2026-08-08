import asyncio
from playwright.async_api import async_playwright

async def test_chart():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto('https://verdischain.com/dex/')
        await page.wait_for_timeout(2000)

        # Switch to price chart tab
        await page.click('#tabBtn-chart')
        await page.wait_for_timeout(1000)

        # Inspect canvas
        canvas = await page.query_selector('#priceChart')
        if canvas:
            box = await canvas.bounding_box()
            print("Canvas bounding box:", box)

            # Check canvas width/height properties vs bounding box
            width_prop = await canvas.evaluate('el => el.width')
            height_prop = await canvas.evaluate('el => el.height')
            print(f"Canvas internal size: width={width_prop}, height={height_prop}")

        # Check timeframe buttons
        tf_btns = await page.query_selector_all('.tf-btn')
        print(f"Timeframe buttons count: {len(tf_btns)}")
        for btn in tf_btns:
            txt = await btn.inner_text()
            print(f"Clicking timeframe button: {txt}")
            await btn.click()
            await page.wait_for_timeout(300)

        # Check pair dropdown in Chart section
        chart_pair_select = await page.query_selector('#pane-chart select')
        if chart_pair_select:
            val = await chart_pair_select.input_value()
            print(f"Chart pair select current value: {val}")
            await chart_pair_select.select_option('VRDX/TREE')
            await page.wait_for_timeout(500)
            # Check if chart redrew or price updated
            price_text = await page.inner_text('#pane-chart .mono') if await page.query_selector('#pane-chart .mono') else 'N/A'
            print(f"After selecting VRDX/TREE, chart price display: {price_text}")

        await page.screenshot(path="chart_tab.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_chart())
