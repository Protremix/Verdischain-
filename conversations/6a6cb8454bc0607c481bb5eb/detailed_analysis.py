import asyncio
import json
import os
from playwright.async_api import async_playwright

EVAL_JS = """
() => {
    const headerNavLinks = Array.from(document.querySelectorAll('header a, nav a')).map(a => ({
        text: a.innerText ? a.innerText.trim().replace(/\\n/g, ' ') : '',
        href: a.getAttribute('href'),
        fullHref: a.href,
        visible: a.offsetWidth > 0 && a.offsetHeight > 0
    }));

    const footerLinks = Array.from(document.querySelectorAll('footer a')).map(a => ({
        text: a.innerText ? a.innerText.trim().replace(/\\n/g, ' ') : '',
        href: a.getAttribute('href')
    }));

    const brokenImages = Array.from(document.querySelectorAll('img')).filter(img => !img.complete || img.naturalWidth === 0).map(img => ({
        src: img.src,
        alt: img.alt,
        className: img.className
    }));

    const canvases = Array.from(document.querySelectorAll('canvas')).map(c => {
        const ctx2d = c.getContext('2d');
        const ctxWebgl = c.getContext('webgl') || c.getContext('webgl2');
        return {
            id: c.id,
            class: c.className,
            width: c.width,
            height: c.height,
            clientWidth: c.clientWidth,
            clientHeight: c.clientHeight,
            has2dCtx: !!ctx2d,
            hasWebglCtx: !!ctxWebgl
        };
    });

    let cssTexts = '';
    try {
        const stylesheets = Array.from(document.styleSheets);
        stylesheets.forEach(s => {
            try {
                Array.from(s.cssRules).forEach(r => cssTexts += r.cssText + ' ');
            } catch(e) {}
        });
    } catch(e) {}

    const hexColorRegex = /#(?:[0-9a-fA-F]{3,4}){1,2}\\b/g;
    const matches = cssTexts.match(hexColorRegex) || [];
    const colorCounts = {};
    matches.forEach(c => colorCounts[c.toLowerCase()] = (colorCounts[c.toLowerCase()] || 0) + 1);

    const neonRegex = /#caff33|#00ff00|#39ff14|#a3e635|#4ade80|#22c55e|#16a34a|#15803d|#166534/gi;
    const matchesGreen = cssTexts.match(neonRegex) || [];

    const mainElements = Array.from(document.querySelectorAll('header, main section, footer, card, div[class*="card"], div[class*="box"]'));
    const elementBoxes = mainElements.map(el => {
        const r = el.getBoundingClientRect();
        return {
            tag: el.tagName,
            class: el.className.slice(0, 50),
            top: r.top,
            bottom: r.bottom,
            left: r.left,
            right: r.right,
            width: r.width,
            height: r.height,
            text: el.innerText ? el.innerText.slice(0, 30).replace(/\\n/g, ' ') : ''
        };
    });

    const buttons = Array.from(document.querySelectorAll('button, a.btn, a[class*="button"], a[class*="bg-"]')).map(b => ({
        text: b.innerText ? b.innerText.trim().replace(/\\n/g, ' ') : '',
        bg: window.getComputedStyle(b).backgroundColor,
        color: window.getComputedStyle(b).color,
        href: b.getAttribute('href')
    }));

    return {
        headerNavLinks,
        footerLinks,
        brokenImages,
        canvases,
        colorCounts,
        matchesGreen,
        elementBoxes: elementBoxes.slice(0, 20),
        buttons: buttons.slice(0, 15)
    };
}
"""

async def inspect_details():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})

        pages = [
            ("Homepage", "https://verdischain.com/"),
            ("Explorer", "https://verdischain.com/explorer/"),
            ("DEX", "https://verdischain.com/dex/"),
            ("Wallet", "https://verdischain.com/wallet/"),
            ("Validators", "https://verdischain.com/validators/"),
            ("Token Sale", "https://verdischain.com/sale/"),
            ("Tokenomics", "https://verdischain.com/tokenomics/"),
            ("Faucet", "https://verdischain.com/faucet/"),
            ("Eco Dashboard", "https://verdischain.com/eco/"),
            ("Whitepaper", "https://verdischain.com/whitepaper/"),
            ("Docs", "https://verdischain.com/docs/"),
        ]

        detailed_data = {}

        for name, url in pages:
            page = await context.new_page()
            
            logs = []
            requests_info = []

            page.on("console", lambda msg: logs.append({"type": msg.type, "text": msg.text, "location": str(msg.location)}))
            page.on("response", lambda res: requests_info.append({"url": res.url, "status": res.status}) if res.status >= 400 else None)

            res = await page.goto(url, wait_until="networkidle", timeout=20000)
            await page.wait_for_timeout(2000)

            data = await page.evaluate(EVAL_JS)

            detailed_data[name] = {
                "url": url,
                "status": res.status if res else None,
                "title": await page.title(),
                "logs": logs,
                "failed_requests": requests_info,
                "data": data
            }

            await page.close()

        await browser.close()

        with open("detailed_audit.json", "w") as f:
            json.dump(detailed_data, f, indent=2)
        print("Detailed audit complete.")

if __name__ == "__main__":
    asyncio.run(inspect_details())
