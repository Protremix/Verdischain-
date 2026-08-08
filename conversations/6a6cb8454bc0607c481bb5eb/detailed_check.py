import json
import urllib.request
import urllib.error
from playwright.sync_api import sync_playwright

def run_deep_check():
    report = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # -------------------------------------------------------------
        # DESKTOP VIEWPORT (1280 x 800)
        # -------------------------------------------------------------
        page_d = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        d_console = []
        d_errors = []
        page_d.on("console", lambda msg: d_console.append(f"[{msg.type}] {msg.text}"))
        page_d.on("pageerror", lambda err: d_errors.append(str(err)))
        
        page_d.goto('https://verdischain.com/', wait_until='networkidle')
        page_d.wait_for_timeout(3000)
        
        # Take full page and hero screenshots
        page_d.screenshot(path='desktop_full.png', full_page=True)
        page_d.screenshot(path='desktop_viewport.png')
        
        # -------------------------------------------------------------
        # MOBILE VIEWPORT (375 x 812)
        # -------------------------------------------------------------
        page_m = browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True)
        
        m_console = []
        m_errors = []
        page_m.on("console", lambda msg: m_console.append(f"[{msg.type}] {msg.text}"))
        page_m.on("pageerror", lambda err: m_errors.append(str(err)))
        
        page_m.goto('https://verdischain.com/', wait_until='networkidle')
        page_m.wait_for_timeout(3000)
        
        page_m.screenshot(path='mobile_full.png', full_page=True)
        page_m.screenshot(path='mobile_viewport.png')
        
        # Extract HTML / Text / DOM info from Desktop
        page_html = page_d.content()
        body_text = page_d.inner_text('body')
        
        # 1. Nav Links
        nav_elements = page_d.evaluate("""() => {
            const navs = Array.from(document.querySelectorAll('nav a, header a, [class*="nav"] a'));
            return navs.map(a => ({
                text: a.innerText.trim(),
                href: a.getAttribute('href'),
                outerHTML: a.outerHTML,
                rect: a.getBoundingClientRect()
            }));
        }""")
        
        # All links on page
        all_links = page_d.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a'));
            return anchors.map(a => ({
                text: a.innerText.trim(),
                href: a.getAttribute('href'),
                url: a.href,
                outerHTML: a.outerHTML
            }));
        }""")
        
        # 2. Hero floating cards / elements
        hero_elements = page_d.evaluate("""() => {
            // Find elements in hero section
            const heroSection = document.querySelector('header, section, .hero, [class*="hero"]') || document.body;
            const allElements = Array.from(document.querySelectorAll('*'));
            
            // Get floating cards, badges, glass cards, stat cards in hero
            const cardCandidates = allElements.filter(el => {
                const cls = (el.className || '').toString();
                const id = (el.id || '').toString();
                return (cls.includes('card') || cls.includes('floating') || cls.includes('badge') || cls.includes('glass') || cls.includes('hero-') || cls.includes('absolute'))
                    && el.children.length < 10
                    && el.getBoundingClientRect().height > 20
                    && el.getBoundingClientRect().width > 20;
            });
            
            return cardCandidates.map(c => {
                const rect = c.getBoundingClientRect();
                return {
                    tagName: c.tagName,
                    class: c.className,
                    id: c.id,
                    text: c.innerText.trim().replace(/\\n/g, ' '),
                    rect: { top: rect.top, bottom: rect.bottom, left: rect.left, right: rect.right, width: rect.width, height: rect.height, x: rect.x, y: rect.y },
                    zIndex: getComputedStyle(c).zIndex,
                    position: getComputedStyle(c).position
                };
            });
        }""")
        
        # 3. Stats section elements
        stats_data = page_d.evaluate("""() => {
            const elems = Array.from(document.querySelectorAll('*'));
            // Look for stat boxes, numbers, values
            const statBoxes = elems.filter(el => {
                const cls = (el.className || '').toString();
                return cls.includes('stat') || cls.includes('metric') || cls.includes('grid') || cls.includes('counter');
            });
            return statBoxes.map(el => ({
                class: el.className,
                text: el.innerText.trim()
            }));
        }""")
        
        # 4. 3D Floating Cluster / Canvas elements
        canvases_d = page_d.evaluate("""() => {
            const items = Array.from(document.querySelectorAll('canvas, svg, [class*="3d"], [class*="cluster"], [id*="canvas"], [id*="three"], [class*="three"], [class*="spline"]'));
            return items.map(c => {
                const rect = c.getBoundingClientRect();
                const style = getComputedStyle(c);
                return {
                    tagName: c.tagName,
                    id: c.id,
                    className: c.className,
                    rect: { top: rect.top, bottom: rect.bottom, left: rect.left, right: rect.right, width: rect.width, height: rect.height },
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity
                };
            });
        }""")

        canvases_m = page_m.evaluate("""() => {
            const items = Array.from(document.querySelectorAll('canvas, svg, [class*="3d"], [class*="cluster"], [id*="canvas"], [id*="three"], [class*="three"], [class*="spline"]'));
            return items.map(c => {
                const rect = c.getBoundingClientRect();
                const style = getComputedStyle(c);
                return {
                    tagName: c.tagName,
                    id: c.id,
                    className: c.className,
                    rect: { top: rect.top, bottom: rect.bottom, left: rect.left, right: rect.right, width: rect.width, height: rect.height },
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity
                };
            });
        }""")

        # Check WebGL/Three.js animation activity on mobile vs desktop
        anim_test_d = page_d.evaluate("""async () => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return { hasCanvas: false };
            // Read webgl context or animation state
            return {
                hasCanvas: true,
                width: canvas.width,
                height: canvas.height,
                styleWidth: canvas.style.width,
                styleHeight: canvas.style.height
            };
        }""")

        anim_test_m = page_m.evaluate("""async () => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return { hasCanvas: false };
            return {
                hasCanvas: true,
                width: canvas.width,
                height: canvas.height,
                styleWidth: canvas.style.width,
                styleHeight: canvas.style.height
            };
        }""")

        browser.close()

        report['d_console'] = d_console
        report['d_errors'] = d_errors
        report['m_console'] = m_console
        report['m_errors'] = m_errors
        report['body_text'] = body_text
        report['nav_elements'] = nav_elements
        report['all_links'] = all_links
        report['hero_elements'] = hero_elements
        report['stats_data'] = stats_data
        report['canvases_d'] = canvases_d
        report['canvases_m'] = canvases_m
        report['anim_d'] = anim_test_d
        report['anim_m'] = anim_test_m

    with open('deep_report.json', 'w') as f:
        json.dump(report, f, indent=2)

run_deep_check()
