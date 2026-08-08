import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        await page.goto('https://verdischain.com/wallet/', wait_until='networkidle')

        # Mock apiCall or mock transactions
        res = await page.evaluate("""async () => {
            // Override apiCall to return dummy transactions
            window.apiCall = async (path) => {
                if (path.includes('/transactions')) {
                    return [
                        { from: '3an...', to: '3an...', amount: '1000000000', block: 100, timestamp: Date.now() }
                    ];
                }
                return null;
            };
            try {
                await loadHistory();
                return "SUCCESS";
            } catch (e) {
                return "ERROR: " + e.message;
            }
        }""")

        print("loadHistory with mock transactions result:", res)
        print("Page errors:", page_errors)

        await browser.close()

asyncio.run(run())
