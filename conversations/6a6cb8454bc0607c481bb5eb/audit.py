import asyncio
import json
import os
import re
from playwright.async_api import async_playwright

PAGES = [
    {"name": "Homepage", "url": "https://verdischain.com/"},
    {"name": "Explorer", "url": "https://verdischain.com/explorer/"},
    {"name": "DEX", "url": "https://verdischain.com/dex/"},
    {"name": "Wallet", "url": "https://verdischain.com/wallet/"},
    {"name": "Validators", "url": "https://verdischain.com/validators/"},
    {"name": "Token Sale", "url": "https://verdischain.com/sale/"},
    {"name": "Tokenomics", "url": "https://verdischain.com/tokenomics/"},
    {"name": "Faucet", "url": "https://verdischain.com/faucet/"},
    {"name": "Eco Dashboard", "url": "https://verdischain.com/eco/"},
    {"name": "Whitepaper", "url": "https://verdischain.com/whitepaper/"},
    {"name": "Docs", "url": "https://verdischain.com/docs/"},
]

os.makedirs("screenshots", exist_ok=True)

EVAL_JS = """
() => {
    const pageText = document.body ? document.body.innerText : '';
    const bodyHtml = document.body ? document.body.innerHTML : '';
    
    const allNodes = document.querySelectorAll('*');
    let neonGreenCount = 0;
    let darkGreenCount = 0;
    let neonElements = [];
    let neonInStyles = [];

    const htmlLower = bodyHtml.toLowerCase();
    const hasNeonHex = htmlLower.includes('#caff33') || htmlLower.includes('rgb(202, 255, 51)') || htmlLower.includes('202,255,51');
    
    try {
        for (let styleSheet of document.styleSheets) {
            try {
                for (let rule of styleSheet.cssRules) {
                    if (rule.cssText && (rule.cssText.toLowerCase().includes('#caff33') || rule.cssText.toLowerCase().includes('202, 255, 51'))) {
                        neonInStyles.push(rule.cssText.slice(0, 100));
                    }
                }
            } catch (e) {}
        }
    } catch (e) {}

    allNodes.forEach(el => {
        try {
            const style = window.getComputedStyle(el);
            const color = style.color || '';
            const bg = style.backgroundColor || '';
            const border = style.borderColor || '';

            if (color.includes('202, 255, 51') || bg.includes('202, 255, 51') || border.includes('202, 255, 51')) {
                neonGreenCount++;
                neonElements.push(el.tagName + '.' + el.className + ' | ' + (el.innerText ? el.innerText.slice(0, 30) : ''));
            }
            if (color.includes('22, 163, 74') || bg.includes('22, 163, 74') || border.includes('22, 163, 74')) {
                darkGreenCount++;
            }
        } catch (e) {}
    });

    const navLinks = Array.from(document.querySelectorAll('nav a, header a')).map(a => ({
        text: a.innerText.trim(),
        href: a.getAttribute('href'),
        fullHref: a.href
    }));

    const footerLinks = Array.from(document.querySelectorAll('footer a')).map(a => ({
        text: a.innerText.trim(),
        href: a.getAttribute('href')
    }));

    const canvases = Array.from(document.querySelectorAll('canvas')).map(c => ({
        width: c.width,
        height: c.height,
        clientWidth: c.clientWidth,
        clientHeight: c.clientHeight,
        webglContext: !!(c.getContext('webgl') || c.getContext('webgl2'))
    }));

    const sections = Array.from(document.querySelectorAll('section, main > div, div[class*="section"], div[class*="container"]'));
    const emptySections = [];
    sections.forEach((sec, idx) => {
        const rect = sec.getBoundingClientRect();
        const text = sec.innerText.trim();
        if (rect.height > 100 && text.length === 0) {
            emptySections.push({ index: idx, class: sec.className, height: rect.height });
        }
    });

    const headings = Array.from(document.querySelectorAll('h1, h2, h3, p, button, a')).map(el => {
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return {
            tag: el.tagName,
            text: el.innerText ? el.innerText.slice(0, 40).replace(/\\n/g, ' ') : '',
            color: style.color,
            bg: style.backgroundColor,
            fontSize: style.fontSize,
            visible: rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden',
            top: rect.top,
            bottom: rect.bottom,
            height: rect.height
        };
    });

    return {
        pageLength: pageText.length,
        previewText: pageText.slice(0, 300).replace(/\\s+/g, ' '),
        hasNeonHex,
        neonGreenCount,
        darkGreenCount,
        neonInStyles,
        neonElements: neonElements.slice(0, 10),
        navLinks,
        footerLinks,
        canvases,
        emptySections,
        headingCount: headings.length,
        headingsSample: headings.slice(0, 15)
    };
}
"""

async def audit_page(context, page_info):
    page = await context.new_page()
    
    console_logs = []
    failed_requests = []
    
    page.on("console", lambda msg: console_logs.append({
        "type": msg.type,
        "text": msg.text,
        "location": str(msg.location)
    }))
    
    page.on("requestfailed", lambda req: failed_requests.append({
        "url": req.url,
        "failure": str(req.failure)
    }))
    
    page.on("response", lambda res: failed_requests.append({
        "url": res.url,
        "status": res.status
    }) if res.status >= 400 else None)

    url = page_info["url"]
    name = page_info["name"]
    slug = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())

    print(f"--- Auditing: {name} ({url}) ---")
    
    response = None
    try:
        response = await page.goto(url, wait_until="networkidle", timeout=20000)
    except Exception as e:
        print(f"Goto timeout/error for {url}: {e}")
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=10000)
        except Exception as e2:
            print(f"Secondary goto error: {e2}")

    await page.wait_for_timeout(3000)

    http_status = response.status if response else "Unknown"
    title = await page.title()

    viewport_path = f"screenshots/{slug}_viewport.png"
    full_path = f"screenshots/{slug}_full.png"
    await page.screenshot(path=viewport_path)
    try:
        await page.screenshot(path=full_path, full_page=True)
    except Exception as e:
        print(f"Full page screenshot failed for {name}: {e}")
        full_path = viewport_path

    analysis = await page.evaluate(EVAL_JS)

    await page.close()

    return {
        "name": name,
        "url": url,
        "http_status": http_status,
        "title": title,
        "viewport_path": viewport_path,
        "full_path": full_path,
        "console_logs": console_logs,
        "failed_requests": failed_requests,
        "analysis": analysis
    }

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        results = []
        for page_info in PAGES:
            res = await audit_page(context, page_info)
            results.append(res)
            
        await browser.close()
        
        with open("audit_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("Audit run complete! Saved to audit_results.json")

if __name__ == "__main__":
    asyncio.run(main())
