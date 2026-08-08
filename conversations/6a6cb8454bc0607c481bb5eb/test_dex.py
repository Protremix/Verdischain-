import asyncio
from playwright.async_api import async_playwright, ConsoleMessage, Request, Response

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        console_logs = []
        page_errors = []
        network_requests = []
        failed_requests = []

        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        
        def handle_response(response: Response):
            if response.status >= 400:
                failed_requests.append(f"{response.status} {response.url}")
            network_requests.append(f"{response.status} {response.request.method} {response.url}")

        page.on("response", handle_response)

        print("Navigating to https://verdischain.com/dex/ ...")
        res = await page.goto('https://verdischain.com/dex/', wait_until='networkidle', timeout=30000)
        print("Page title:", await page.title())
        print("HTTP status:", res.status if res else "No response")

        await page.wait_for_timeout(3000)

        # Take desktop screenshot
        await page.screenshot(path='desktop_full.png', full_page=True)
        await page.screenshot(path='desktop_viewport.png', full_page=False)

        # HTML dump for analysis
        content = await page.content()
        with open("dex_page.html", "w") as f:
            f.write(content)

        print(f"Captured {len(console_logs)} console logs, {len(page_errors)} page errors, {len(failed_requests)} failed requests.")

        print("\n--- Console Errors / Warnings ---")
        for log in console_logs:
            if "error" in log.lower() or "warn" in log.lower() or "fail" in log.lower():
                print(log)

        print("\n--- Page Uncaught JS Errors ---")
        for err in page_errors:
            print(err)

        print("\n--- Failed Network Requests (>=400) ---")
        for freq in failed_requests:
            print(freq)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(audit())
