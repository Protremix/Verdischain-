import asyncio
from playwright.async_api import async_playwright
import json

urls = [
    "https://verdischain.com/docs/?nocache=50013",
    "https://verdischain.com/blog/?nocache=50014",
    "https://verdischain.com/developers/?nocache=50015",
    "https://verdischain.com/download/?nocache=50016",
    "https://verdischain.com/status/?nocache=50017"
]

async def analyze():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for url in urls:
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            console_logs = []
            page.on("console", lambda msg: console_logs.append(f"CONSOLE {msg.type}: {msg.text}"))
            
            failed_requests = []
            page.on("requestfailed", lambda req: failed_requests.append(f"FAILED REQ: {req.url} - {req.failure}"))
            
            response = await page.goto(url, wait_until="networkidle")
            status = response.status if response else "NO_RESPONSE"
            title = await page.title()
            
            # Extract content
            text = await page.inner_text("body")
            
            # Extract links
            links = await page.eval_on_selector_all("a", "elements => elements.map(e => ({text: e.innerText.trim(), href: e.getAttribute('href'), outerHTML: e.outerHTML}))")
            
            # Check overflow
            overflow = await page.evaluate("() => ({scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth})")
            
            print(f"=== URL: {url} ===")
            print(f"Status: {status}, Title: {title}")
            print(f"Console log count: {len(console_logs)}")
            print(f"Failed requests count: {len(failed_requests)}")
            print(f"Links count: {len(links)}")
            print(f"Overflow: {overflow}")
            print("-" * 50)
            
            await context.close()

        await browser.close()

asyncio.run(analyze())
