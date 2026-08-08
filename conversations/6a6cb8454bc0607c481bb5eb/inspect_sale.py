import asyncio
from playwright.async_api import async_playwright, Page
import json
import os
import urllib.request
import urllib.parse

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        console_logs = []
        network_errors = []

        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("response", lambda res: network_errors.append(f"{res.status} {res.url}") if res.status >= 400 else None)

        url = "https://verdischain.com/sale/?nocache=50005"
        print(f"Navigating to {url}...")
        response = await page.goto(url, wait_until="networkidle")

        print(f"Page response status: {response.status}")

        # Desktop screenshot
        await page.screenshot(path="screenshot_desktop.png", full_page=True)

        # Tablet screenshot
        await page.set_viewport_size({'width': 768, 'height': 1024})
        await page.screenshot(path="screenshot_tablet.png", full_page=True)

        # Mobile screenshot
        await page.set_viewport_size({'width': 375, 'height': 812})
        await page.screenshot(path="screenshot_mobile.png", full_page=True)

        # Back to desktop
        await page.set_viewport_size({'width': 1280, 'height': 800})

        # Extract basic page data
        title = await page.title()
        content = await page.content()

        # Extract all text content structured by selector / tags
        text_content = await page.evaluate("""() => {
            return document.body.innerText;
        }""")

        # Extract all links
        links = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText.trim(),
                href: a.getAttribute('href'),
                full_href: a.href,
                location: a.closest('nav') ? 'nav' : (a.closest('footer') ? 'footer' : 'body')
            }));
        }""")

        # Extract all images
        images = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img')).map(img => ({
                src: img.getAttribute('src'),
                alt: img.getAttribute('alt'),
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight,
                complete: img.complete,
                visible: img.offsetWidth > 0 && img.offsetHeight > 0
            }));
        }""")

        # Extract layout details of sections and phase grid
        layout_info = await page.evaluate("""() => {
            const elements = [];
            const allNodes = document.querySelectorAll('*');
            
            // Phase grid cards
            const phaseGrid = document.querySelector('.phase-grid, .phases-grid, .grid, [class*="phase"], [class*="grid"]');
            
            // Check bounding boxes for overlapping visible elements
            const visibleElems = Array.from(document.querySelectorAll('body *')).filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden' && window.getComputedStyle(el).display !== 'none';
            });

            return {
                phaseGridHTML: phaseGrid ? phaseGrid.outerHTML : null,
                phaseGridStyle: phaseGrid ? window.getComputedStyle(phaseGrid).gridTemplateColumns : null,
                elementCount: visibleElems.length
            };
        }""")

        # Save HTML
        with open("page_dom.html", "w") as f:
            f.write(content)

        # Save extracted text
        with open("extracted_text.txt", "w") as f:
            f.write(text_content)

        print("\n--- CONSOLE LOGS ---")
        for log in console_logs:
            print(log)

        print("\n--- NETWORK ERRORS ---")
        for err in network_errors:
            print(err)

        print("\n--- LINKS ---")
        print(json.dumps(links, indent=2))

        print("\n--- IMAGES ---")
        print(json.dumps(images, indent=2))

        print("\n--- LAYOUT INFO ---")
        print(json.dumps(layout_info, indent=2))

        await browser.close()

asyncio.run(audit())
