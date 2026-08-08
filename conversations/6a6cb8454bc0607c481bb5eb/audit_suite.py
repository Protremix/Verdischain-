import json
import urllib.request
import urllib.error
import time
from playwright.sync_api import sync_playwright

def run_suite():
    out = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # 1. DESKTOP ANALYSIS (1280x800)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append({'type': msg.type, 'text': msg.text}))
        
        page.goto('https://verdischain.com/', wait_until='networkidle')
        page.wait_for_timeout(3000) # wait for counters / animations
        
        # Check specific stat elements in the 4 grid counters
        counter_grid = page.evaluate("""() => {
            const gridCards = Array.from(document.querySelectorAll('.grid > div, [class*="stat"], [class*="counter"], [class*="metric"]'));
            return gridCards.map(c => ({
                text: c.innerText.replace(/\\n/g, ' | '),
                rect: c.getBoundingClientRect()
            }));
        }""")
        out['counter_grid'] = counter_grid

        # Check Hero floating elements overlap
        hero_cards = page.evaluate("""() => {
            const allElements = Array.from(document.querySelectorAll('header *, section:first-of-type *'));
            const glassCards = allElements.filter(el => {
                const cls = String(el.className || '');
                const isCard = cls.includes('card') || cls.includes('glass') || cls.includes('floating') || cls.includes('bg-') || cls.includes('border');
                const rect = el.getBoundingClientRect();
                return isCard && rect.width > 50 && rect.height > 30 && rect.top < 1000;
            });
            
            return glassCards.map((c, idx) => {
                const rect = c.getBoundingClientRect();
                return {
                    id: idx,
                    class: String(c.className),
                    text: c.innerText.replace(/\\n/g, ' ').substring(0, 100),
                    rect: { top: rect.top, bottom: rect.bottom, left: rect.left, right: rect.right, width: rect.width, height: rect.height, x: rect.x, y: rect.y }
                };
            });
        }""")
        out['hero_cards'] = hero_cards

        # Get exact top nav items desktop
        top_nav_desktop = page.evaluate("""() => {
            const navLinks = Array.from(document.querySelectorAll('header nav a, nav a, header a'));
            return navLinks.map(a => ({
                text: a.innerText.trim(),
                href: a.getAttribute('href'),
                visible: a.getBoundingClientRect().width > 0
            }));
        }""")
        out['top_nav_desktop'] = top_nav_desktop

        # Check pallet occurrences
        pallet_occurrences = page.evaluate("""() => {
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
            const matches = [];
            let node;
            while (node = walker.nextNode()) {
                if (node.nodeValue.toLowerCase().includes('pallet')) {
                    matches.push({
                        text: node.nodeValue.trim(),
                        parentTag: node.parentElement.tagName,
                        parentClass: String(node.parentElement.className),
                        parentContext: node.parentElement.parentElement ? node.parentElement.parentElement.innerText.replace(/\\n/g, ' ') : ''
                    });
                }
            }
            return matches;
        }""")
        out['pallet_occurrences'] = pallet_occurrences

        # Check links
        links = page.evaluate("""() => {
            const anchors = Array.from(document.querySelectorAll('a[href]'));
            return anchors.map(a => ({
                text: a.innerText.trim().replace(/\\n/g, ' '),
                href: a.getAttribute('href'),
                fullUrl: a.href
            }));
        }""")
        out['links'] = links

        # 2. MOBILE ANALYSIS (375x812)
        page_m = browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True)
        page_m.goto('https://verdischain.com/', wait_until='networkidle')
        page_m.wait_for_timeout(3000)

        # Top nav mobile
        top_nav_mobile = page_m.evaluate("""() => {
            const navLinks = Array.from(document.querySelectorAll('header nav a, nav a, header a'));
            return navLinks.map(a => ({
                text: a.innerText.trim(),
                href: a.getAttribute('href'),
                visible: a.getBoundingClientRect().width > 0
            }));
        }""")
        out['top_nav_mobile'] = top_nav_mobile

        # Mobile menu toggle button check
        mobile_menu_btn = page_m.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, [class*="menu"], [class*="hamburger"], [class*="toggle"]'));
            return btns.map(b => ({
                text: b.innerText.trim(),
                class: String(b.className),
                rect: b.getBoundingClientRect(),
                visible: b.getBoundingClientRect().width > 0
            }));
        }""")
        out['mobile_menu_btn'] = mobile_menu_btn

        # Mobile hero 3D canvas position and visibility
        mobile_canvas = page_m.evaluate("""() => {
            const canvas = document.querySelector('canvas#hero-canvas, canvas');
            if (!canvas) return null;
            const rect = canvas.getBoundingClientRect();
            const style = getComputedStyle(canvas);
            return {
                id: canvas.id,
                rect: { top: rect.top, bottom: rect.bottom, left: rect.left, right: rect.right, width: rect.width, height: rect.height, x: rect.x, y: rect.y },
                display: style.display,
                visibility: style.visibility,
                opacity: style.opacity,
                parentRect: canvas.parentElement ? canvas.parentElement.getBoundingClientRect() : null
            };
        }""")
        out['mobile_canvas'] = mobile_canvas

        browser.close()

    # 3. HTTP LINK CHECK
    print("Checking HTTP status of links...")
    link_results = []
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    
    unique_urls = {}
    for l in out['links']:
        url = l['fullUrl']
        if url not in unique_urls:
            unique_urls[url] = l['text']

    for url, txt in unique_urls.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            res = urllib.request.urlopen(req, timeout=10)
            link_results.append({'url': url, 'text': txt, 'status': res.status, 'error': None})
        except urllib.error.HTTPError as e:
            link_results.append({'url': url, 'text': txt, 'status': e.code, 'error': str(e)})
        except Exception as e:
            link_results.append({'url': url, 'text': txt, 'status': 0, 'error': str(e)})

    out['link_check'] = link_results

    with open('suite_results.json', 'w') as f:
        json.dump(out, f, indent=2)

run_suite()
