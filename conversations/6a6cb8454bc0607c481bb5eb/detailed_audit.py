import asyncio
from playwright.async_api import async_playwright
import json
import re
import urllib.request
import urllib.error

async def run_detailed_audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # We will test at desktop 1280x800
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto("https://verdischain.com/sale/?nocache=50005", wait_until="networkidle")

        # 1. CSS & Layout Analysis
        # Check .phases-grid styling and computed CSS
        phases_grid_info = await page.evaluate("""() => {
            const grid = document.querySelector('.phases-grid');
            if (!grid) return null;
            const style = window.getComputedStyle(grid);
            const children = Array.from(grid.children);
            const childRects = children.map((c, idx) => {
                const r = c.getBoundingClientRect();
                return { idx, class: c.className, x: r.x, y: r.y, width: r.width, height: r.height };
            });
            return {
                display: style.display,
                gridTemplateColumns: style.gridTemplateColumns,
                gap: style.gap,
                childRects: childRects
            };
        }""")

        # Check overlapping elements
        overlaps = await page.evaluate("""() => {
            function isOverlapping(rect1, rect2) {
                return !(rect1.right <= rect2.left || 
                         rect1.left >= rect2.right || 
                         rect1.bottom <= rect2.top || 
                         rect1.top >= rect2.bottom);
            }

            // Check floating cards / hero / text overlap
            const elems = Array.from(document.querySelectorAll('body *')).filter(el => {
                const r = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                return r.width > 10 && r.height > 10 && style.visibility !== 'hidden' && style.display !== 'none' && style.opacity !== '0';
            });

            const issues = [];
            // Check specifically cards, floating elements, text blocks
            const floatCards = Array.from(document.querySelectorAll('.float-card'));
            for (let i = 0; i < floatCards.length; i++) {
                for (let j = i + 1; j < floatCards.length; j++) {
                    const r1 = floatCards[i].getBoundingClientRect();
                    const r2 = floatCards[j].getBoundingClientRect();
                    if (isOverlapping(r1, r2)) {
                        issues.push({
                            type: 'float_card_overlap',
                            elem1: floatCards[i].className + ' ' + floatCards[i].innerText.slice(0, 30),
                            elem2: floatCards[j].className + ' ' + floatCards[j].innerText.slice(0, 30),
                            r1: {x: r1.x, y: r1.y, w: r1.width, h: r1.height},
                            r2: {x: r2.x, y: r2.y, w: r2.width, h: r2.height}
                        });
                    }
                }
            }
            return issues;
        }""")

        # Extract all section texts and HTML snippets
        full_text = await page.evaluate("document.body.innerText")
        
        # Check hero h1, text, prices, stats, tables, FAQ, etc.
        page_structure = await page.evaluate("""() => {
            const sections = [];
            document.querySelectorAll('section, header, nav, footer, div[class*="section"], div[class*="hero"]').forEach(s => {
                sections.push({
                    className: s.className,
                    id: s.id,
                    text: s.innerText
                });
            });
            return sections;
        }""")

        # Check images on page
        images_status = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img')).map(img => ({
                src: img.src,
                alt: img.alt,
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight,
                complete: img.complete,
                boundingClientRect: img.getBoundingClientRect()
            }));
        }""")

        await browser.close()

        print("=== PHASES GRID INFO ===")
        print(json.dumps(phases_grid_info, indent=2))

        print("=== OVERLAPS ===")
        print(json.dumps(overlaps, indent=2))

        print("=== IMAGES STATUS ===")
        print(json.dumps(images_status, indent=2))

asyncio.run(run_detailed_audit())
