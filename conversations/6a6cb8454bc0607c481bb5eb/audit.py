import asyncio
import json
import os
import urllib.parse
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

os.makedirs("screenshots/desktop", exist_ok=True)
os.makedirs("screenshots/mobile", exist_ok=True)

async def check_links(page, base_url):
    links = await page.eval_on_selector_all("a[href]", "elements => elements.map(e => ({href: e.getAttribute('href'), text: (e.innerText || e.textContent || '').trim()}))")
    broken_links = []
    checked = set()
    
    urls_to_check = []
    for l in links:
        href = l['href']
        if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
            continue
        full_url = urllib.parse.urljoin(base_url, href)
        if full_url not in checked:
            checked.add(full_url)
            urls_to_check.append((href, full_url, l['text']))
            
    context = page.context
    for href, full_url, text in urls_to_check:
        try:
            res = await context.request.get(full_url, timeout=5000)
            if res.status >= 400:
                broken_links.append({'href': href, 'full_url': full_url, 'text': text, 'status': res.status})
        except Exception as e:
            broken_links.append({'href': href, 'full_url': full_url, 'text': text, 'error': str(e)})
            
    return links, broken_links

async def audit_page(p, name, url):
    print(f"\n--- Auditing {name}: {url} ---")
    results = {
        "name": name,
        "url": url,
        "http_status": None,
        "title": None,
        "console_errors": [],
        "failed_requests": [],
        "desktop_overflow": False,
        "mobile_overflow": False,
        "broken_links": [],
        "total_links": 0,
        "images": [],
        "missing_alt_images": 0,
        "broken_images": [],
        "interactive_elements": []
    }

    browser = await p.chromium.launch(headless=True)
    
    # 1. Desktop Audit
    d_context = await browser.new_context(viewport={"width": 1280, "height": 800})
    d_page = await d_context.new_page()
    
    # Capture console & failed requests
    d_page.on("console", lambda msg: results["console_errors"].append(f"[Desktop Console {msg.type}] {msg.text}") if msg.type in ["error", "warning"] else None)
    d_page.on("requestfailed", lambda req: results["failed_requests"].append(f"[Desktop Request Failed] {req.url} - {req.failure}"))

    try:
        response = await d_page.goto(url, wait_until="networkidle", timeout=15000)
        results["http_status"] = response.status if response else "No response"
    except Exception as e:
        results["http_status"] = f"Error: {e}"
        try:
            response = await d_page.goto(url, wait_until="domcontentloaded", timeout=10000)
            results["http_status"] = response.status if response else "Error"
        except Exception:
            pass

    results["title"] = await d_page.title()
    await d_page.screenshot(path=f"screenshots/desktop/{name}.png", full_page=True)

    # Check overflow desktop
    d_overflow = await d_page.evaluate("() => ({scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth, overflow: document.documentElement.scrollWidth > window.innerWidth})")
    results["desktop_overflow"] = d_overflow

    # Images
    images = await d_page.eval_on_selector_all("img", "imgs => imgs.map(i => ({src: i.src, alt: i.alt, naturalWidth: i.naturalWidth, naturalHeight: i.naturalHeight}))")
    results["images"] = images
    for img in images:
        if not img.get("alt"):
            results["missing_alt_images"] += 1
        if img.get("naturalWidth") == 0:
            results["broken_images"].append(img.get("src"))

    # Links check
    links, broken_links = await check_links(d_page, url)
    results["total_links"] = len(links)
    results["broken_links"] = broken_links

    # Buttons / Inputs / Forms
    buttons = await d_page.eval_on_selector_all("button, input, form, select, textarea", "elems => elems.map(e => ({tag: e.tagName, type: e.type, id: e.id, class: e.className, text: (e.innerText || e.value || '').trim()}))")
    results["interactive_elements"] = buttons

    # Text content
    text_content = await d_page.evaluate("() => document.body.innerText")
    
    # 2. Mobile Audit (375px width)
    m_context = await browser.new_context(
        viewport={"width": 375, "height": 812}, 
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    )
    m_page = await m_context.new_page()
    m_page.on("console", lambda msg: results["console_errors"].append(f"[Mobile Console {msg.type}] {msg.text}") if msg.type in ["error", "warning"] else None)

    try:
        await m_page.goto(url, wait_until="networkidle", timeout=15000)
    except Exception:
        await m_page.goto(url, wait_until="domcontentloaded", timeout=10000)

    await m_page.screenshot(path=f"screenshots/mobile/{name}.png", full_page=True)
    m_overflow = await m_page.evaluate("() => ({scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth, overflow: document.documentElement.scrollWidth > window.innerWidth})")
    results["mobile_overflow"] = m_overflow

    await browser.close()
    return results, text_content

async def main():
    async with async_playwright() as p:
        all_results = {}
        all_texts = {}
        for name, url in PAGES:
            res, text = await audit_page(p, name, url)
            all_results[name] = res
            all_texts[name] = text
        
        with open("audit_results.json", "w") as f:
            json.dump(all_results, f, indent=2)
        with open("audit_texts.json", "w") as f:
            json.dump(all_texts, f, indent=2)
        print("\nAudit completed! Results saved.")

asyncio.run(main())
