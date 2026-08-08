import asyncio
from playwright.async_api import async_playwright

async def run_audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # 1. Desktop Audit (1280x800)
        # -------------------------------------------------------------
        context_desktop = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context_desktop.new_page()

        console_logs = []
        page_errors = []

        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        print("--- Navigating Desktop ---")
        response = await page.goto('https://verdischain.com/wallet/', wait_until='networkidle')
        print(f"Status: {response.status}")

        await page.screenshot(path='desktop_initial.png', full_page=True)

        # Test Generate Wallet
        print("--- Testing Generate Wallet ---")
        try:
            # Click "Create New Wallet" button
            create_btn = page.locator("button:has-text('Create New Wallet')").first
            if await create_btn.is_visible():
                await create_btn.click()
                await page.wait_for_timeout(500)
                await page.screenshot(path='desktop_create_modal.png')
                
                # Click "Generate Wallet" inside the form
                gen_btn = page.locator("button:has-text('Generate New Wallet')").first
                if await gen_btn.is_visible():
                    await gen_btn.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path='desktop_after_generate.png', full_page=True)
        except Exception as e:
            print("Error testing Generate Wallet:", e)

        # Print console logs & errors after wallet generation
        print("\nConsole logs (Desktop):")
        for log in console_logs:
            print("  ", log)
        print("\nPage errors (Desktop):")
        for err in page_errors:
            print("  ", err)

        await context_desktop.close()

        # -------------------------------------------------------------
        # 2. Mobile Audit (375x812 - iPhone X/12/13 mini)
        # -------------------------------------------------------------
        context_mobile = await browser.new_context(
            viewport={'width': 375, 'height': 812},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
        )
        page_m = await context_mobile.new_page()

        console_logs_m = []
        page_errors_m = []
        page_m.on("console", lambda msg: console_logs_m.append(f"[{msg.type}] {msg.text}"))
        page_m.on("pageerror", lambda err: page_errors_m.append(str(err)))

        print("\n--- Navigating Mobile (375px) ---")
        await page_m.goto('https://verdischain.com/wallet/', wait_until='networkidle')
        await page_m.screenshot(path='mobile_initial.png', full_page=True)

        # Test Hamburger menu
        hamburger = page_m.locator('.hamburger')
        if await hamburger.is_visible():
            await hamburger.click()
            await page_m.wait_for_timeout(300)
            await page_m.screenshot(path='mobile_nav_open.png')

        await context_mobile.close()
        await browser.close()

asyncio.run(run_audit())
