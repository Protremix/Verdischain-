import asyncio
from playwright.async_api import async_playwright

async def run_mobile():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Mobile viewport 375x812 (iPhone 12/13 mini / X / 11 Pro)
        context = await browser.new_context(
            viewport={'width': 375, 'height': 812},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
        )
        page = await context.new_page()

        print("--- Navigating Mobile (375px) ---")
        await page.goto('https://verdischain.com/wallet/', wait_until='networkidle')

        # Screenshot 1: Mobile Initial / Unauthenticated
        await page.screenshot(path="mobile_01_auth.png", full_page=True)

        # Test Hamburger menu
        print("Testing Hamburger menu...")
        hamburger = page.locator('.hamburger')
        if await hamburger.is_visible():
            await hamburger.click()
            await page.wait_for_timeout(300)
            await page.screenshot(path="mobile_02_menu_open.png")
            # Close hamburger menu
            await hamburger.click()
            await page.wait_for_timeout(300)

        # Check horizontal overflow on mobile
        scroll_width = await page.evaluate("document.documentElement.scrollWidth")
        inner_width = await page.evaluate("window.innerWidth")
        print(f"Scroll width: {scroll_width}px, Inner width: {inner_width}px")

        # Create wallet to check mobile dashboard layout
        print("Creating wallet on mobile...")
        await page.click('.auth-card:first-child')
        await page.wait_for_timeout(300)
        await page.screenshot(path="mobile_03_create_form.png")

        await page.click('button:has-text("Generate New Wallet")')
        await page.wait_for_timeout(1000)

        # Screenshot 4: Mobile Dashboard (Send Tab)
        await page.screenshot(path="mobile_04_dash_send.png", full_page=True)

        # Test Stake Tab on Mobile
        print("Switching to Stake Tab on Mobile...")
        await page.click('button.tab-btn:has-text("Stake")')
        await page.wait_for_timeout(1000)
        await page.screenshot(path="mobile_05_dash_stake.png", full_page=True)

        # Inspect layout of validator items on 375px
        validator_item_box = await page.evaluate("""() => {
            const item = document.querySelector('.validator-item');
            if (!item) return null;
            const rightDiv = item.children[1];
            return {
                itemWidth: item.clientWidth,
                itemScrollWidth: item.scrollWidth,
                rightDivWidth: rightDiv ? rightDiv.clientWidth : 0,
                rightDivScrollWidth: rightDiv ? rightDiv.scrollWidth : 0
            };
        }""")
        print("Validator item metrics on mobile:", validator_item_box)

        # Check Receive Tab on Mobile
        print("Switching to Receive Tab on Mobile...")
        await page.click('button.tab-btn:has-text("Receive")')
        await page.wait_for_timeout(500)
        await page.screenshot(path="mobile_06_dash_receive.png")

        await browser.close()

asyncio.run(run_mobile())
