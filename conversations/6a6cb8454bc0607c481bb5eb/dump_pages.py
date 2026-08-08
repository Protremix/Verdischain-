import asyncio
from playwright.async_api import async_playwright
import os
import json

urls = {
    "docs": "https://verdischain.com/docs/?nocache=50013",
    "blog": "https://verdischain.com/blog/?nocache=50014",
    "developers": "https://verdischain.com/developers/?nocache=50015",
    "download": "https://verdischain.com/download/?nocache=50016",
    "status": "https://verdischain.com/status/?nocache=50017"
}

os.makedirs("dumps", exist_ok=True)

async def dump():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for name, url in urls.items():
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            page = await context.new_page()
            
            logs = []
            page.on("console", lambda m: logs.append({'type': m.type, 'text': m.text}))
            failed = []
            page.on("requestfailed", lambda r: failed.append({'url': r.url, 'failure': str(r.failure)}))
            
            res = await page.goto(url, wait_until="networkidle")
            
            # Save html
            html = await page.content()
            with open(f"dumps/{name}.html", "w", encoding="utf-8") as f:
                f.write(html)
                
            # Save inner text
            text = await page.inner_text("body")
            with open(f"dumps/{name}.txt", "w", encoding="utf-8") as f:
                f.write(text)
                
            # Screenshots (desktop & mobile)
            await page.screenshot(path=f"dumps/{name}_desktop.png", full_page=True)
            
            # Mobile screenshot
            await page.set_viewport_size({'width': 375, 'height': 812})
            await page.screenshot(path=f"dumps/{name}_mobile.png", full_page=True)
            
            # Extract links detail
            links_data = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a, button, form')).map(el => {
                    return {
                        tag: el.tagName,
                        text: el.innerText.trim(),
                        href: el.getAttribute('href'),
                        action: el.getAttribute('action'),
                        onclick: el.getAttribute('onclick'),
                        outerHTML: el.outerHTML,
                        isVisible: el.offsetWidth > 0 && el.offsetHeight > 0
                    };
                });
            }""")
            
            # Extract images
            images_data = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('img')).map(el => {
                    return {
                        src: el.getAttribute('src'),
                        alt: el.getAttribute('alt'),
                        naturalWidth: el.naturalWidth,
                        naturalHeight: el.naturalHeight,
                        complete: el.complete,
                        outerHTML: el.outerHTML
                    };
                });
            }""")

            info = {
                'url': url,
                'status': res.status if res else None,
                'title': await page.title(),
                'logs': logs,
                'failed_requests': failed,
                'links': links_data,
                'images': images_data
            }
            with open(f"dumps/{name}_info.json", "w", encoding="utf-8") as f:
                json.dump(info, f, indent=2)
                
            print(f"Dumped {name}")
            await context.close()
            
        await browser.close()

asyncio.run(dump())
