import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        console_logs = []
        page_errors = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        await page.goto('https://verdischain.com/wallet/', wait_until='networkidle')

        # 1. Test secp import and window.secp properties
        secp_info = await page.evaluate("""() => {
            return {
                hasSecp: typeof window.secp !== 'undefined',
                secpKeys: window.secp ? Object.keys(window.secp) : [],
                utilsKeys: window.secp && window.secp.utils ? Object.keys(window.secp.utils) : []
            };
        }""")
        print("1. SECP INFO:", secp_info)

        # 2. Test Create Wallet Click
        await page.evaluate("showCreate()")
        await page.wait_for_timeout(300)
        await page.screenshot(path="screenshot_create_form.png")

        # Click Generate New Wallet
        print("Calling generateWallet()...")
        await page.evaluate("generateWallet()")
        await page.wait_for_timeout(1000)
        await page.screenshot(path="screenshot_dashboard.png")

        # 3. Check Wallet State in localStorage
        wallet_ls = await page.evaluate("localStorage.getItem('verdis_wallet')")
        print("3. LOCALSTORAGE WALLET:", wallet_ls)

        # 4. Check Receive tab & showReceive() call
        print("Calling showReceive()...")
        try:
            res = await page.evaluate("showReceive()")
            print("showReceive() success")
        except Exception as e:
            print("showReceive() EXCEPTION:", e)

        # 5. Check History Tab
        print("Calling showTab('history')...")
        try:
            await page.evaluate("showTab('history')")
            print("showTab('history') success")
        except Exception as e:
            print("showTab('history') EXCEPTION:", e)

        # 6. Check Stake Tab
        print("Calling showTab('stake')...")
        try:
            await page.evaluate("showTab('stake')")
            print("showTab('stake') success")
        except Exception as e:
            print("showTab('stake') EXCEPTION:", e)

        # 7. Test Send Transaction button
        print("Calling sendTransaction()...")
        try:
            await page.evaluate("sendTransaction()")
            print("sendTransaction() call finished")
        except Exception as e:
            print("sendTransaction() EXCEPTION:", e)

        # Wait a bit and collect all console logs / errors
        await page.wait_for_timeout(1000)
        print("\n=== CONSOLE LOGS ===")
        for l in console_logs:
            print("  ", l)

        print("\n=== PAGE ERRORS ===")
        for e in page_errors:
            print("  ", e)

        await browser.close()

asyncio.run(run())
