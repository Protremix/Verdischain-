import asyncio
import json
from playwright.async_api import async_playwright

INSPECT_JS = """
() => {
    // 1. Footer links detailed list
    const footers = Array.from(document.querySelectorAll('footer a')).map(a => ({
        text: a.innerText.trim(),
        href: a.getAttribute('href')
    }));

    // 2. DEX Chart container inspect
    const priceChart = document.getElementById('priceChart');
    const priceChartParent = priceChart ? priceChart.parentElement : null;
    const priceChartDetails = priceChart ? {
        id: priceChart.id,
        w: priceChart.width,
        h: priceChart.height,
        parentTag: priceChartParent.tagName,
        parentClass: priceChartParent.className,
        parentW: priceChartParent.clientWidth,
        parentH: priceChartParent.clientHeight,
        parentDisplay: window.getComputedStyle(priceChartParent).display
    } : null;

    // 3. Faucet stats inspect
    const faucetStatsEl = document.querySelector('[id*="stat"], [class*="stat"]');
    const faucetText = document.body ? document.body.innerText : '';

    // 4. Color check in inline styles and computed styles for all elements
    const neonElements = [];
    const allElements = document.querySelectorAll('*');
    allElements.forEach(el => {
        const style = window.getComputedStyle(el);
        const bg = style.backgroundColor;
        const color = style.color;
        const border = style.borderColor;
        const fill = style.fill;
        const stroke = style.stroke;
        
        // Neon green #caff33 is rgb(202, 255, 51)
        if (bg.includes('202, 255, 51') || color.includes('202, 255, 51') || border.includes('202, 255, 51') || fill.includes('202, 255, 51') || stroke.includes('202, 255, 51')) {
            neonElements.push({ tag: el.tagName, class: el.className, text: el.innerText ? el.innerText.slice(0, 30) : '' });
        }
    });

    // 5. Check all links destination validation (relative vs absolute)
    const allLinks = Array.from(document.querySelectorAll('a')).map(a => ({
        text: a.innerText.trim().replace(/\\n/g, ' '),
        href: a.getAttribute('href'),
        fullHref: a.href
    }));

    // 6. Homepage Hero Canvas JS inspection
    const heroCanvas = document.getElementById('hero-canvas');
    let heroCanvasDetails = null;
    if (heroCanvas) {
        heroCanvasDetails = {
            width: heroCanvas.width,
            height: heroCanvas.height,
            clientWidth: heroCanvas.clientWidth,
            clientHeight: heroCanvas.clientHeight,
            style: heroCanvas.getAttribute('style')
        };
    }

    return {
        footerLinks: footers,
        priceChartDetails,
        neonElements,
        allLinksCount: allLinks.length,
        allLinks: allLinks.slice(0, 30),
        heroCanvasDetails
    };
}
"""

async def run_inspection():
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

        results = {}
        for name, url in pages:
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_timeout(2000)
            res = await page.evaluate(INSPECT_JS)
            results[name] = res
            await page.close()

        await browser.close()

        with open("deep_inspection.json", "w") as f:
            json.dump(results, f, indent=2)
        print("Deep inspection complete.")

if __name__ == "__main__":
    asyncio.run(run_inspection())
