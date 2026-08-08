import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Mobile viewport
        mobile_page = await browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
        await mobile_page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        print("=== MOBILE OVERFLOW / LAYOUT CHECKS ===")
        overflow_elements = await mobile_page.evaluate("""
            () => {
                const docWidth = document.documentElement.offsetWidth;
                const elements = document.querySelectorAll('*');
                const overflowing = [];
                elements.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.right > docWidth + 2) {
                        overflowing.push({
                            tag: el.tagName,
                            class: el.className,
                            id: el.id,
                            right: rect.right,
                            docWidth: docWidth,
                            text: el.innerText ? el.innerText.substring(0, 50) : ''
                        });
                    }
                });
                return overflowing;
            }
        """)
        print(f"Total elements exceeding viewport width on mobile ({len(overflow_elements)}):")
        for o in overflow_elements[:15]:
            print(o)

        print("\n=== MOBILE FONT SIZE CHECKS ===")
        font_sizes = await mobile_page.evaluate("""
            () => {
                const elements = document.querySelectorAll('p, span, div, a, li, h1, h2, h3, h4, th, td');
                const smallFonts = [];
                elements.forEach(el => {
                    if (el.children.length === 0 && el.innerText.trim().length > 0) {
                        const style = window.getComputedStyle(el);
                        const fontSize = parseFloat(style.fontSize);
                        if (fontSize < 12) {
                            smallFonts.push({
                                tag: el.tagName,
                                class: el.className,
                                text: el.innerText.substring(0, 60),
                                fontSize: style.fontSize,
                                parentClass: el.parentElement ? el.parentElement.className : ''
                            });
                        }
                    }
                });
                return smallFonts;
            }
        """)
        print(f"Elements with font-size < 12px on mobile ({len(font_sizes)}):")
        for f in font_sizes[:20]:
            print(f)

        # Let's inspect all headings and key text font sizes on mobile and desktop
        print("\n=== FONT SIZE DISTRIBUTION (MOBILE) ===")
        all_font_summary = await mobile_page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                const fontCounts = {};
                elements.forEach(el => {
                    if (el.children.length === 0 && el.innerText.trim().length > 0) {
                        const style = window.getComputedStyle(el);
                        const fs = style.fontSize;
                        fontCounts[fs] = (fontCounts[fs] || 0) + 1;
                    }
                });
                return fontCounts;
            }
        """)
        print("Font sizes used on mobile:", all_font_summary)

        # Desktop font sizes
        desktop_page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await desktop_page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        desktop_font_summary = await desktop_page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                const fontCounts = {};
                elements.forEach(el => {
                    if (el.children.length === 0 && el.innerText.trim().length > 0) {
                        const style = window.getComputedStyle(el);
                        const fs = style.fontSize;
                        fontCounts[fs] = (fontCounts[fs] || 0) + 1;
                    }
                });
                return fontCounts;
            }
        """)
        print("Font sizes used on desktop:", desktop_font_summary)

        await browser.close()

asyncio.run(audit())
