import asyncio
import json
from playwright.async_api import async_playwright

PAGES = [
    ("faucet", "https://verdischain.com/faucet/"),
    ("referral", "https://verdischain.com/referral/"),
    ("incentives", "https://verdischain.com/incentives/"),
    ("docs", "https://verdischain.com/docs/"),
    ("contact", "https://verdischain.com/contact/"),
    ("api", "https://verdischain.com/api/"),
    ("terms", "https://verdischain.com/terms/"),
    ("privacy", "https://verdischain.com/privacy/")
]

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for name, url in PAGES:
            print(f"==================================================")
            print(f"PAGE: {name} - {url}")
            
            # Context for mobile and desktop
            page = await browser.new_page(viewport={"width": 1280, "height": 800})
            
            requests_log = []
            page.on("response", lambda res: requests_log.append((res.status, res.url)))
            
            await page.goto(url, wait_until="networkidle")
            
            # Check 502s or non-200 subresources
            bad_subresources = [r for r in requests_log if r[0] >= 400]
            if bad_subresources:
                print("  Failed Subresources:", bad_subresources)
                
            # Get full html
            html = await page.content()
            
            # Check all links on the page (all <a> tags)
            all_links = await page.eval_on_selector_all("a", "elems => elems.map(e => ({href: e.getAttribute('href'), text: (e.innerText || e.textContent || '').trim(), outer: e.outerHTML}))")
            print(f"  Total <a> links on page: {len(all_links)}")
            
            # Check form / input elements
            forms = await page.eval_on_selector_all("form, input, button, select, textarea", "elems => elems.map(e => ({tag: e.tagName, type: e.getAttribute('type'), id: e.id, name: e.getAttribute('name'), placeholder: e.getAttribute('placeholder'), text: (e.innerText || e.value || '').trim()}))")
            print(f"  Interactive Elements ({len(forms)}):", json.dumps(forms, indent=2))
            
            # Check text
            text = await page.evaluate("() => document.body.innerText")
            print(f"  Text Snippet (first 300 chars): {text[:300]}...")
            
            # Test interactivity or forms if any
            if name == "faucet":
                # Check what happens when clicking faucet button or submitting address
                print("  Faucet page details:")
                # Look for input or button
                input_box = await page.query_selector("input")
                button = await page.query_selector("button")
                print("  Input present:", bool(input_box), "Button present:", bool(button))
                if button:
                    btn_text = await button.inner_text()
                    print("  Button text:", btn_text)

            if name == "contact":
                print("  Contact form inputs:", forms)

            if name == "referral":
                print("  Referral elements:", forms)
                
            # Check mobile layout element overflow specifics
            m_page = await browser.new_page(viewport={"width": 375, "height": 812})
            await m_page.goto(url, wait_until="networkidle")
            
            overflowing_elements = await m_page.evaluate("""() => {
                const elems = document.querySelectorAll('*');
                const overflowing = [];
                for (let el of elems) {
                    if (el.scrollWidth > el.clientWidth && el.clientWidth > 0) {
                        overflowing.append ? overflowing.push({
                            tag: el.tagName,
                            class: el.className,
                            id: el.id,
                            scrollWidth: el.scrollWidth,
                            clientWidth: el.clientWidth,
                            text: el.innerText ? el.innerText.substring(0, 50) : ''
                        }) : null;
                    }
                }
                return overflowing;
            }""")
            if overflowing_elements:
                print("  Mobile Overflowing Elements:", len(overflowing_elements))
                for oe in overflowing_elements[:5]:
                    print("   -", oe)
                    
            await page.close()
            await m_page.close()
            
        await browser.close()

asyncio.run(inspect())
