import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Mobile Page
        m_ctx = await browser.new_context(
            viewport={'width': 375, 'height': 812},
            is_mobile=True,
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
        )
        mobile_page = await m_ctx.new_page()
        await mobile_page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        # Desktop Page
        d_ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        desktop_page = await d_ctx.new_page()
        await desktop_page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        print("=================== MOBILE OVERFLOW ELEMENTS ===================")
        overflows = await mobile_page.evaluate("""
            () => {
                const docWidth = document.documentElement.clientWidth;
                const elements = document.querySelectorAll('*');
                const list = [];
                elements.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.right > docWidth + 2) {
                        list.push({
                            tag: el.tagName,
                            class: el.className,
                            id: el.id,
                            rectRight: Math.round(rect.right),
                            docWidth: docWidth,
                            textSnippet: (el.innerText || '').substring(0, 40).replace(/\\n/g, ' ')
                        });
                    }
                });
                return list;
            }
        """)
        for o in overflows:
            print(f"Tag: {o['tag']}, Class: {o['class']}, Right: {o['rectRight']}px > {o['docWidth']}px | Text: {o['textSnippet']}")

        print("\n=================== SMALL FONT SIZES (< 12px) ===================")
        small_fonts = await mobile_page.evaluate("""
            () => {
                const elements = document.querySelectorAll('*');
                const list = [];
                elements.forEach(el => {
                    if (el.children.length === 0 && el.innerText && el.innerText.trim().length > 0) {
                        const style = window.getComputedStyle(el);
                        const fs = parseFloat(style.fontSize);
                        if (fs < 12) {
                            list.push({
                                tag: el.tagName,
                                class: el.className,
                                text: el.innerText.trim().substring(0, 50),
                                fontSize: style.fontSize,
                                line: style.lineHeight,
                                parentClass: el.parentElement ? el.parentElement.className : ''
                            });
                        }
                    }
                });
                return list;
            }
        """)
        for sf in small_fonts:
            print(f"[{sf['fontSize']}] Tag: {sf['tag']}, Class: '{sf['class']}', Parent: '{sf['parentClass']}' | Text: '{sf['text']}'")

        print("\n=================== HERO SECTION VISUAL CARDS ON MOBILE ===================")
        hero_vis = await mobile_page.evaluate("""
            () => {
                const cards = document.querySelectorAll('.wp-doc, .wp-card, .wp-team, .wp-roadmap, .wp-carbon, .float-tag, .hero-lime-circle');
                return Array.from(cards).map(el => {
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    return {
                        class: el.className,
                        rect: { x: Math.round(rect.x), y: Math.round(rect.y), w: Math.round(rect.width), h: Math.round(rect.height) },
                        display: style.display,
                        visibility: style.visibility,
                        opacity: style.opacity
                    };
                });
            }
        """)
        for hv in hero_vis:
            print(hv)

        print("\n=================== PIE CHART MATCH & LEGEND ===================")
        pie_match = await desktop_page.evaluate("""
            () => {
                // Table / Card items
                const distItems = Array.from(document.querySelectorAll('.distribution-card, .token-card, .distribution-item, [class*="distribut"]')).map(el => el.innerText);
                
                // SVG segments
                const svg = document.querySelector('.pie-svg');
                if (!svg) return { error: 'No .pie-svg' };
                const segs = Array.from(svg.querySelectorAll('.pie-seg')).map(s => ({
                    stroke: s.getAttribute('stroke'),
                    dasharray: s.getAttribute('stroke-dasharray'),
                    dashoffset: s.getAttribute('stroke-dashoffset')
                }));
                return { segs, distItems };
            }
        """)
        print(pie_match)

        print("\n=================== ROADMAP VS VESTING DETAILS ===================")
        rm_details = await desktop_page.evaluate("""
            () => {
                const rmText = document.querySelector('#roadmap, .roadmap-timeline, [class*="roadmap"]')?.innerText;
                const vestText = document.querySelector('#vesting, [class*="vesting"]')?.innerText;
                return { rmText, vestText };
            }
        """)
        print("Roadmap text:", rm_details['rmText'])
        print("Vesting text:", rm_details['vestText'])

        await browser.close()

asyncio.run(audit())
