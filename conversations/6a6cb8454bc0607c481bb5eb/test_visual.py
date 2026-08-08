import asyncio
import os
import json
from playwright.async_api import async_playwright

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/tmp/pw-browsers"

async def audit_visuals():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        viewports = [
            ("desktop_1440", 1440, 900, False),
            ("desktop_1920", 1920, 1080, False),
            ("tablet_768", 768, 1024, False),
            ("mobile_375", 375, 812, True)
        ]
        
        issues = []
        
        for name, w, h, is_mob in viewports:
            ctx = await browser.new_context(viewport={'width': w, 'height': h}, is_mobile=is_mob)
            page = await ctx.new_page()
            await page.goto("https://verdischain.com/wallet/?nocache=50004", wait_until="networkidle")
            
            # Check horizontal overflow
            scroll_width = await page.evaluate("document.documentElement.scrollWidth")
            client_width = await page.evaluate("document.documentElement.clientWidth")
            if scroll_width > client_width:
                issues.append(f"[{name}] Horizontal scrollbar detected! scrollWidth ({scroll_width}) > clientWidth ({client_width})")
                
            # Check for overlapping visible elements in auth state
            overlaps = await page.evaluate("""() => {
                let els = Array.from(document.querySelectorAll('body *')).filter(e => {
                    let rect = e.getBoundingClientRect();
                    let style = window.getComputedStyle(e);
                    return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none' && style.opacity !== '0';
                });
                
                // Compare pairs of leaf/significant elements
                let leafEls = els.filter(e => e.children.length === 0 || e.tagName === 'BUTTON' || e.tagName === 'A' || e.tagName === 'H1' || e.tagName === 'H3' || e.tagName === 'P' || e.tagName === 'INPUT' || e.tagName === 'TEXTAREA');
                let found = [];
                for (let i = 0; i < leafEls.length; i++) {
                    for (let j = i + 1; j < leafEls.length; j++) {
                        let r1 = leafEls[i].getBoundingClientRect();
                        let r2 = leafEls[j].getBoundingClientRect();
                        
                        // Check if leafEls[i] contains leafEls[j] or vice versa
                        if (leafEls[i].contains(leafEls[j]) || leafEls[j].contains(leafEls[i])) continue;
                        
                        // Check box overlap
                        let overlap = !(r1.right <= r2.left || r1.left >= r2.right || r1.bottom <= r2.top || r1.top >= r2.bottom);
                        if (overlap) {
                            // ignore background or pseudo or fixed cursor glow
                            if (leafEls[i].id === 'cursor-glow' || leafEls[j].id === 'cursor-glow') continue;
                            if (leafEls[i].id === 'scroll-bar' || leafEls[j].id === 'scroll-bar') continue;
                            found.append({
                                el1: leafEls[i].tagName + '.' + leafEls[i].className + '#' + leafEls[i].id,
                                text1: leafEls[i].innerText?.slice(0, 20),
                                el2: leafEls[j].tagName + '.' + leafEls[j].className + '#' + leafEls[j].id,
                                text2: leafEls[j].innerText?.slice(0, 20),
                                rect1: r1,
                                rect2: r2
                            });
                        }
                    }
                }
                return found;
            }""")
            
            if overlaps:
                for ov in overlaps:
                    issues.append(f"[{name}] Overlap between {ov['el1']} ('{ov['text1']}') and {ov['el2']} ('{ov['text2']}')")

            # Check footer visual styles / position
            footer_box = await page.evaluate("""() => {
                let f = document.querySelector('footer.footer');
                if (!f) return null;
                let r = f.getBoundingClientRect();
                let style = window.getComputedStyle(f);
                return {
                    width: r.width,
                    height: r.height,
                    top: r.top,
                    marginTop: style.marginTop,
                    padding: style.padding,
                    borderTop: style.borderTop
                };
            }""")
            
            # Click "Create New Wallet" to check form layout
            await page.click("text=Create New Wallet")
            await page.wait_for_timeout(300)
            await page.screenshot(path=f"screenshot_{name}_create_form.png")
            
            # Generate wallet and test dashboard
            await page.click("text=Generate New Wallet")
            await page.wait_for_timeout(1200) # wait for dashboard load
            await page.screenshot(path=f"screenshot_{name}_dashboard.png")
            
            # Check tabs in dashboard
            # Receive tab
            await page.click("button:has-text('Receive')")
            await page.wait_for_timeout(300)
            await page.screenshot(path=f"screenshot_{name}_dash_receive.png")
            
            # History tab
            await page.click("button:has-text('History')")
            await page.wait_for_timeout(300)
            await page.screenshot(path=f"screenshot_{name}_dash_history.png")
            
            # Stake tab
            await page.click("button:has-text('Stake')")
            await page.wait_for_timeout(300)
            await page.screenshot(path=f"screenshot_{name}_dash_stake.png")

            await ctx.close()

        await browser.close()
        print("\n--- VISUAL AUDIT ISSUES ---")
        for iss in issues:
            print(iss)

asyncio.run(audit_visuals())
