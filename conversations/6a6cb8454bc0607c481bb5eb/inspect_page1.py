import asyncio
import json
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()

        console_logs = []
        page_errors = []
        failed_requests = []

        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        page.on("requestfailed", lambda req: failed_requests.append(f"{req.url} ({req.failure})"))

        response = await page.goto('https://verdischain.com/api/?nocache=50024', wait_until='networkidle')
        print(f"HTTP Status: {response.status}")
        
        # Take desktop screenshot
        await page.screenshot(path='page1_desktop.png', full_page=True)

        # Take mobile screenshot
        await page.set_viewport_size({'width': 375, 'height': 812})
        await page.screenshot(path='page1_mobile.png', full_page=True)

        # Restore desktop
        await page.set_viewport_size({'width': 1440, 'height': 900})

        # Get HTML content
        html_content = await page.content()

        print("\n--- Console Logs ---")
        for log in console_logs:
            print(log)

        print("\n--- Page Errors ---")
        for err in page_errors:
            print(err)

        print("\n--- Failed Network Requests ---")
        for req in failed_requests:
            print(req)

        # Check visual overlap / bounds with JS
        overlap_issues = await page.evaluate('''() => {
            const elements = Array.from(document.querySelectorAll('header, nav, main, section, footer, div, h1, h2, h3, p, a, button, table, tr, td, th, pre, code'));
            const issues = [];
            
            // Check overflow / clipping
            for (let el of elements) {
                if (el.offsetWidth < el.scrollWidth) {
                    issues.append({
                        type: 'horizontal_overflow',
                        tag: el.tagName,
                        id: el.id,
                        className: el.className,
                        text: el.innerText ? el.innerText.substring(0, 50) : '',
                        clientWidth: el.clientWidth,
                        scrollWidth: el.scrollWidth
                    });
                }
            }
            return issues;
        }''')
        print("\n--- Overflows / Visual Issues ---")
        print(json.dumps(overlap_issues, indent=2))

        await browser.close()

asyncio.run(run())
