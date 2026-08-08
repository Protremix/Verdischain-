import asyncio
from playwright.async_api import async_playwright

async def detailed_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Test 1: Desktop Viewport
        context_desktop = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page_d = await context_desktop.new_page()

        logs_d = []
        errors_d = []
        requests_d = []

        page_d.on("console", lambda msg: logs_d.append(f"[{msg.type}] {msg.text}"))
        page_d.on("pageerror", lambda err: errors_d.append(str(err)))
        page_d.on("response", lambda res: requests_d.append(f"{res.status} {res.request.method} {res.url}"))

        await page_d.goto('https://verdischain.com/dex/', wait_until='networkidle')
        await page_d.wait_for_timeout(3000)

        # Let's inspect console errors
        print("=== DESKTOP CONSOLE LOGS ===")
        for l in logs_d:
            print(l)

        print("\n=== DESKTOP PAGE ERRORS ===")
        for e in errors_d:
            print(e)

        print("\n=== NETWORK REQUESTS TO RPC OR APIS ===")
        for r in requests_d:
            if "rpc" in r or "api" in r or "verdis" in r:
                print(r)

        await page_d.screenshot(path="desktop_swap.png", full_page=True)

        # Test switching tabs
        tabs = ["swap", "pools", "liquidity", "chart", "history"]
        for tab in tabs:
            tab_btn = page_d.locator(f"#tabBtn-{tab}")
            if await tab_btn.count() > 0:
                await tab_btn.click()
                await page_d.wait_for_timeout(500)
                await page_d.screenshot(path=f"desktop_tab_{tab}.png")
                print(f"Clicked tab: {tab}")
            else:
                print(f"Tab button #tabBtn-{tab} NOT FOUND!")

        # Test 2: Mobile Viewport (375x812 - iPhone X/12/13/14 width)
        context_mobile = await browser.new_context(
            viewport={'width': 375, 'height': 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        )
        page_m = await context_mobile.new_page()
        
        logs_m = []
        errors_m = []
        page_m.on("console", lambda msg: logs_m.append(f"[{msg.type}] {msg.text}"))
        page_m.on("pageerror", lambda err: errors_m.append(str(err)))

        await page_m.goto('https://verdischain.com/dex/', wait_until='networkidle')
        await page_m.wait_for_timeout(3000)

        await page_m.screenshot(path="mobile_swap.png", full_page=True)

        # Check mobile tabs
        for tab in tabs:
            tab_btn = page_m.locator(f"#tabBtn-{tab}")
            if await tab_btn.count() > 0:
                await tab_btn.click()
                await page_m.wait_for_timeout(500)
                await page_m.screenshot(path=f"mobile_tab_{tab}.png")

        print("\n=== MOBILE PAGE ERRORS ===")
        for e in errors_m:
            print(e)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(detailed_test())
