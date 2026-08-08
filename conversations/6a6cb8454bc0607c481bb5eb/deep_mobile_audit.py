import asyncio
from playwright.async_api import async_playwright

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Mobile Page (375px width)
        m_page = await browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True, user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
        await m_page.goto('https://verdischain.com/whitepaper/', wait_until='networkidle')

        # 1. Check Table overflow
        print("=== TABLE OVERFLOW CHECK ===")
        table_overflow = await m_page.evaluate("""
            () => {
                const table = document.querySelector('table');
                if (!table) return 'No table';
                const parent = table.parentElement;
                const parentStyle = window.getComputedStyle(parent);
                const rect = table.getBoundingClientRect();
                return {
                    tableWidth: rect.width,
                    parentWidth: parent.clientWidth,
                    overflowXStyle: parentStyle.overflowX,
                    parentClass: parent.className
                };
            }
        """)
        print("Table overflow info:", table_overflow)

        # 2. Check Hamburger menu toggle
        print("\n=== HAMBURGER MENU CHECK ===")
        hamburger = await m_page.query_selector('.nav-hamburger')
        nav_links = await m_page.query_selector('.nav-links')
        nav_links_vis_before = await nav_links.is_visible() if nav_links else False
        if hamburger:
            await hamburger.click()
            await m_page.wait_for_timeout(300)
            nav_links_vis_after = await nav_links.is_visible() if nav_links else False
            print(f"Hamburger clicked. Links visible before: {nav_links_vis_before}, after: {nav_links_vis_after}")
        else:
            print("No hamburger button found!")

        # 3. Check Hero visual cards on mobile
        print("\n=== HERO VISUAL CARDS DISPLAY ON MOBILE ===")
        hero_display = await m_page.evaluate("""
            () => {
                const right = document.querySelector('.hero-right');
                if (!right) return 'No .hero-right';
                const style = window.getComputedStyle(right);
                const children = Array.from(right.children).map(c => ({
                    class: c.className,
                    display: window.getComputedStyle(c).display
                }));
                return { heroRightDisplay: style.display, children };
            }
        """)
        print(hero_display)

        # 4. Check images and canvas
        print("\n=== BROKEN IMAGES & CANVAS CHECK ===")
        broken_imgs = await m_page.evaluate("""
            () => {
                const imgs = document.querySelectorAll('img');
                return Array.from(imgs).map(img => ({
                    src: img.src,
                    naturalWidth: img.naturalWidth,
                    naturalHeight: img.naturalHeight,
                    complete: img.complete
                })).filter(i => !i.complete || i.naturalWidth === 0);
            }
        """)
        print("Broken images:", broken_imgs)

        # 5. Check all font sizes < 12px and line heights / contrast
        print("\n=== SMALL FONTS (< 12px) ON MOBILE ===")
        small_fonts = await m_page.evaluate("""
            () => {
                const els = document.querySelectorAll('*');
                const smalls = [];
                els.forEach(el => {
                    if (el.children.length === 0 && el.innerText && el.innerText.trim().length > 0) {
                        const style = window.getComputedStyle(el);
                        const fs = parseFloat(style.fontSize);
                        if (fs < 12) {
                            smalls.push({
                                tag: el.tagName,
                                class: el.className,
                                text: el.innerText.trim().substring(0, 40),
                                fontSize: style.fontSize,
                                color: style.color,
                                bg: style.backgroundColor
                            });
                        }
                    }
                });
                return smalls;
            }
        """)
        print(f"Total small font elements: {len(small_fonts)}")
        for sf in small_fonts[:10]:
            print(sf)

        # 6. Check interactive components (Staking calculator)
        print("\n=== STAKING CALCULATOR CHECK ===")
        calc = await m_page.evaluate("""
            () => {
                const stakeInput = document.getElementById('stake-amount');
                const valSelect = document.getElementById('validator-type');
                const daily = document.getElementById('daily-res')?.innerText;
                const monthly = document.getElementById('monthly-res')?.innerText;
                const yearly = document.getElementById('yearly-res')?.innerText;
                return { hasInput: !!stakeInput, hasSelect: !!valSelect, daily, monthly, yearly };
            }
        """)
        print("Staking calc info:", calc)

        await browser.close()

asyncio.run(audit())
