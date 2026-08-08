from playwright.sync_api import sync_playwright
import json

def check_hero_cards():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Desktop
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.goto('https://verdischain.com/', wait_until='networkidle')
        page.wait_for_timeout(2000)
        
        cards = page.evaluate("""() => {
            // Hero section containers
            const hero = document.querySelector('header, section, .hero') || document.body;
            // Get floating cards / badges / glass panels in hero
            const els = Array.from(document.querySelectorAll('*')).filter(el => {
                const cls = String(el.className || '');
                const style = getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return (cls.includes('card') || cls.includes('glass') || cls.includes('badge') || cls.includes('border') || style.position === 'absolute' || cls.includes('absolute'))
                    && rect.width > 40 && rect.height > 20 && rect.top < 800 && rect.left > 0 && rect.width < 1200;
            });
            
            return els.map((el, i) => {
                const rect = el.getBoundingClientRect();
                return {
                    id: i,
                    tag: el.tagName,
                    class: String(el.className),
                    text: el.innerText.replace(/\\n/g, ' | ').substring(0, 80),
                    rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height, top: rect.top, bottom: rect.bottom, left: rect.left, right: rect.right }
                };
            });
        }""")
        
        # Check pairwise overlaps
        overlaps = []
        for i in range(len(cards)):
            for j in range(i+1, len(cards)):
                c1 = cards[i]
                c2 = cards[j]
                r1 = c1['rect']
                r2 = c2['rect']
                
                # If one is ancestor of another in DOM, ignore parent-child overlap
                # Check bounding box intersection
                x_overlap = max(0, min(r1['right'], r2['right']) - max(r1['left'], r2['left']))
                y_overlap = max(0, min(r1['bottom'], r2['bottom']) - max(r1['top'], r2['top']))
                overlap_area = x_overlap * y_overlap
                
                if overlap_area > 100: # non-trivial overlap
                    overlaps.append({
                        'card1': {'id': c1['id'], 'text': c1['text'], 'class': c1['class'], 'rect': r1},
                        'card2': {'id': c2['id'], 'text': c2['text'], 'class': c2['class'], 'rect': r2},
                        'overlap_area': overlap_area
                    })

        print("=== DESKTOP HERO CARDS ===")
        for c in cards:
            print(f"Card {c['id']}: [{c['text']}] at x={c['rect']['x']}, y={c['rect']['y']}, w={c['rect']['width']}, h={c['rect']['height']}")

        print("\n=== DESKTOP OVERLAPS ===")
        print(json.dumps(overlaps, indent=2))
        
        # Mobile check
        page_m = browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True)
        page_m.goto('https://verdischain.com/', wait_until='networkidle')
        page_m.wait_for_timeout(2000)
        
        m_cards = page_m.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('*')).filter(el => {
                const cls = String(el.className || '');
                const style = getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return (cls.includes('card') || cls.includes('glass') || cls.includes('badge') || cls.includes('border') || style.position === 'absolute' || cls.includes('absolute'))
                    && rect.width > 40 && rect.height > 20 && rect.top < 1200 && rect.left >= 0 && rect.width < 375;
            });
            
            return els.map((el, i) => {
                const rect = el.getBoundingClientRect();
                return {
                    id: i,
                    tag: el.tagName,
                    class: String(el.className),
                    text: el.innerText.replace(/\\n/g, ' | ').substring(0, 80),
                    rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height, top: rect.top, bottom: rect.bottom, left: rect.left, right: rect.right }
                };
            });
        }""")
        
        print("\n=== MOBILE HERO CARDS ===")
        for c in m_cards:
            print(f"Card {c['id']}: [{c['text']}] at x={c['rect']['x']}, y={c['rect']['y']}, w={c['rect']['width']}, h={c['rect']['height']}")

        browser.close()

check_hero_cards()
