from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900})
    page.goto('https://verdischain.com/eco/', wait_until='networkidle')
    page.wait_for_timeout(4000)

    # Gather key metrics and text from rendered DOM
    dom_info = page.evaluate('''() => {
        const getTxt = (id) => {
            const el = document.getElementById(id);
            return el ? el.textContent.trim() : null;
        };

        const getSelectorTxt = (sel) => {
            const els = document.querySelectorAll(sel);
            return Array.from(els).map(e => e.textContent.trim());
        };

        return {
            stat_block: getTxt('stat-block'),
            hero_block_num: getTxt('hero-block-num'),
            stat_validators: getTxt('stat-validators'),
            stat_peers: getTxt('stat-peers'),
            nav_network: getTxt('nav-network'),
            data_eco_co2: getSelectorTxt('[data-eco-co2]'),
            data_eco_trees: getSelectorTxt('[data-eco-trees]'),
            data_eco_retired: getSelectorTxt('[data-eco-retired]'),
            hero_badge: getSelectorTxt('.hero-badge'),
            stat_cards: getSelectorTxt('.stat-card'),
            impact_section: getTxt('impact'),
            reforestation_section: getTxt('reforestation'),
            marketplace_section: getTxt('marketplace'),
            certificate_section: getTxt('certificate'),
        };
    }''')

    print("=== RENDERED DOM INFO ===")
    print(json.dumps(dom_info, indent=2))

    browser.close()
