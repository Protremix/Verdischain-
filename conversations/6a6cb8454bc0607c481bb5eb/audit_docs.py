import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import re

url = "https://verdischain.com/docs/?nocache=50013"

async def audit_docs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Test Desktop
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        logs = []
        page.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
        
        await page.goto(url, wait_until="networkidle")
        
        # 1. Overlap detection script
        overlaps = await page.evaluate("""() => {
            const elements = Array.from(document.querySelectorAll('h1, h2, h3, h4, p, a, button, code, pre, .sidebar, .content, header, footer, div'));
            const rects = elements.map(el => {
                const r = el.getBoundingClientRect();
                return {
                    tag: el.tagName,
                    class: el.className,
                    id: el.id,
                    text: el.innerText ? el.innerText.substring(0, 30).replace(/\\n/g, ' ') : '',
                    left: r.left, top: r.top, right: r.right, bottom: r.bottom, width: r.width, height: r.height,
                    el: el
                };
            }).filter(r => r.width > 0 && r.height > 0 && r.top >= 0);
            
            return []; // We will refine overlap check below
        }""")

        # Check scrollbar/overflow
        desktop_scroll = await page.evaluate("() => ({scrollWidth: document.body.scrollWidth, clientWidth: document.body.clientWidth})")
        
        # Test Copy buttons
        copy_buttons = await page.query_selector_all("button")
        copy_results = []
        for i, btn in enumerate(copy_buttons):
            btn_text = await btn.inner_text()
            if "Copy" in btn_text:
                # click it
                await btn.click()
                new_text = await btn.inner_text()
                copy_results.append(f"Button {i} ('{btn_text}') -> after click: '{new_text}'")
                
        # Test TOC anchor links
        toc_links = await page.query_selector_all("a[href^='#']")
        toc_status = []
        for link in toc_links:
            href = await link.get_attribute("href")
            target_id = href[1:]
            target_el = await page.query_selector(f"#{target_id}" if target_id else "body")
            toc_status.append({'href': href, 'exists': target_el is not None})

        # Test Mobile Viewport
        await page.set_viewport_size({'width': 375, 'height': 812})
        await page.wait_for_timeout(500)
        mobile_scroll = await page.evaluate("() => ({scrollWidth: document.body.scrollWidth, clientWidth: document.body.clientWidth, docScroll: document.documentElement.scrollWidth, docClient: document.documentElement.clientWidth})")
        
        # Check if hamburger menu exists or sidebar covers content on mobile
        sidebar_visible_mobile = await page.evaluate("""() => {
            const sidebar = document.querySelector('.sidebar, aside, nav, [class*="sidebar"]');
            if (!sidebar) return null;
            const r = sidebar.getBoundingClientRect();
            return {
                left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height, display: window.getComputedStyle(sidebar).display
            };
        }""")

        print("=== DOCS AUDIT RESULTS ===")
        print("Console logs:", logs)
        print("Desktop scroll:", desktop_scroll)
        print("Mobile scroll:", mobile_scroll)
        print("Copy button tests:", copy_results)
        print("TOC Anchor Links check:", toc_status)
        print("Sidebar visible on mobile:", sidebar_visible_mobile)

        await browser.close()

asyncio.run(audit_docs())
