import asyncio
import os
import urllib.parse
import json
from playwright.async_api import async_playwright

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/tmp/pw-browsers"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Test desktop viewport
        context = await browser.new_context(viewport={'width': 1440, 'height': 900})
        page = await context.new_page()
        
        console_logs = []
        page_errors = []
        failed_requests = []
        
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        page.on("requestfailed", lambda req: failed_requests.append(f"{req.url} - {req.failure}"))

        print("Navigating to https://verdischain.com/wallet/?nocache=50004...")
        response = await page.goto("https://verdischain.com/wallet/?nocache=50004", wait_until="networkidle")
        print(f"Status: {response.status}")
        
        # Save screenshot
        await page.screenshot(path="screenshot_desktop.png", full_page=True)
        print("Desktop screenshot saved.")
        
        # Mobile viewport test
        m_context = await browser.new_context(viewport={'width': 375, 'height': 812}, is_mobile=True)
        m_page = await m_context.new_page()
        await m_page.goto("https://verdischain.com/wallet/?nocache=50004", wait_until="networkidle")
        await m_page.screenshot(path="screenshot_mobile.png", full_page=True)
        print("Mobile screenshot saved.")

        # Extract text content
        body_text = await page.inner_text("body")
        with open("body_text.txt", "w") as f:
            f.write(body_text)
            
        # Extract HTML
        content = await page.content()
        with open("page_content.html", "w") as f:
            f.write(content)
            
        # Extract all links
        links = await page.eval_on_selector_all("a", """elements => elements.map(e => ({
            text: (e.innerText || e.textContent || '').trim(),
            href: e.href,
            raw_href: e.getAttribute('href'),
            target: e.target,
            id: e.id,
            className: e.className
        }))""")
        with open("links.json", "w") as f:
            json.dump(links, f, indent=2)
        
        # Extract all buttons
        buttons = await page.eval_on_selector_all("button", """elements => elements.map(e => ({
            text: (e.innerText || e.textContent || '').trim(),
            id: e.id,
            className: e.className,
            onclick: e.getAttribute('onclick')
        }))""")
        with open("buttons.json", "w") as f:
            json.dump(buttons, f, indent=2)

        # Extract all images
        images = await page.eval_on_selector_all("img", """elements => elements.map(e => ({
            src: e.src,
            raw_src: e.getAttribute('src'),
            alt: e.alt,
            naturalWidth: e.naturalWidth,
            naturalHeight: e.naturalHeight,
            complete: e.complete,
            id: e.id,
            className: e.className
        }))""")
        with open("images.json", "w") as f:
            json.dump(images, f, indent=2)

        print("\n--- CONSOLE LOGS ---")
        for log in console_logs:
            print(log)
            
        print("\n--- PAGE ERRORS ---")
        for err in page_errors:
            print(err)
            
        print("\n--- FAILED REQUESTS ---")
        for req in failed_requests:
            print(req)

        print(f"\nSaved {len(links)} links, {len(buttons)} buttons, {len(images)} images.")

        await browser.close()

asyncio.run(run())
