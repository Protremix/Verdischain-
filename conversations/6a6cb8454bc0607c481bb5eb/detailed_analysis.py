import asyncio
import json
from playwright.async_api import async_playwright

async def run_detailed_analysis():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ----------------------------------------------------
        # FAUCET PAGE
        # ----------------------------------------------------
        p_faucet = await browser.new_page(viewport={"width": 1280, "height": 800})
        f_net = []
        p_faucet.on("response", lambda r: f_net.append((r.status, r.url)))
        await p_faucet.goto("https://verdischain.com/faucet/", wait_until="networkidle")
        faucet_html = await p_faucet.content()
        
        # Test Faucet Button click
        await p_faucet.fill("#faucetAddr", "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY")
        await p_faucet.fill("#captchaA", "10") # 5 + 5 = 10
        await p_faucet.click("#faucetBtn")
        await p_faucet.wait_for_timeout(1000)
        
        faucet_alert = await p_faucet.evaluate("""() => {
            const el = document.querySelector('.alert, #result, #faucetResult, [id*="result"], [class*="result"], [class*="alert"]');
            return el ? el.innerText : (document.body.innerText.includes('Success') || document.body.innerText.includes('Error') ? 'Message updated' : 'No result el');
        }""")
        
        # Mobile view check for hamburger
        m_faucet = await browser.new_page(viewport={"width": 375, "height": 812})
        await m_faucet.goto("https://verdischain.com/faucet/")
        # Test navHamburger click
        nav_btn = await m_faucet.query_selector("#navHamburger")
        nav_works = False
        if nav_btn:
            await nav_btn.click()
            await m_faucet.wait_for_timeout(500)
            nav_visible = await m_faucet.evaluate("() => document.querySelector('.nav-links, nav ul, #navMenu')?.classList.contains('active') || document.querySelector('.nav-links, nav ul, #navMenu')?.offsetHeight > 0")
            nav_works = bool(nav_visible)

        # ----------------------------------------------------
        # REFERRAL PAGE
        # ----------------------------------------------------
        p_ref = await browser.new_page(viewport={"width": 1280, "height": 800})
        await p_ref.goto("https://verdischain.com/referral/", wait_until="networkidle")
        
        # Check copy link button behavior
        copy_btn = await p_ref.query_selector("button:has-text('Copy Link')")
        copy_text_before = await copy_btn.inner_text() if copy_btn else ""
        if copy_btn:
            await copy_btn.click()
            await p_ref.wait_for_timeout(300)
        copy_text_after = await copy_btn.inner_text() if copy_btn else ""
        
        # Check referral calculator math
        # Inputs: calcT1=50, calcAvg=500, calcT2=100, calcT3=200
        # Expected:
        # Tier 1 = 50 * 500 * 10% = $2,500
        # Tier 2 = 100 * 500 * 5% = $2,500
        # Tier 3 = 200 * 500 * 2.5% = $2,500
        # Total = $7,500
        calc_out = await p_ref.evaluate("""() => {
            const totalEl = document.querySelector('#calcTotal, .calc-total, #totalEarnings');
            const body = document.body.innerText;
            return {
                totalEl: totalEl ? totalEl.innerText : null,
                calcSectionText: document.querySelector('.calc-box, #calculator')?.innerText
            };
        }""")

        # ----------------------------------------------------
        # INCENTIVES PAGE
        # ----------------------------------------------------
        p_inc = await browser.new_page(viewport={"width": 1280, "height": 800})
        await p_inc.goto("https://verdischain.com/incentives/", wait_until="networkidle")
        inc_calc = await p_inc.evaluate("""() => {
            const stakeInput = document.querySelector('#calcStake');
            const tierSelect = document.querySelector('#calcTier');
            const boxText = document.querySelector('.calc-box, #calculator, section:nth-of-type(3)')?.innerText;
            return {
                stake: stakeInput ? stakeInput.value : null,
                tier: tierSelect ? tierSelect.value : null,
                boxText: boxText
            };
        }""")

        # ----------------------------------------------------
        # DOCS PAGE
        # ----------------------------------------------------
        p_docs = await browser.new_page(viewport={"width": 1280, "height": 800})
        await p_docs.goto("https://verdischain.com/docs/", wait_until="networkidle")
        
        # Check copy buttons on code blocks
        copy_btns = await p_docs.query_selector_all("button:has-text('Copy')")
        copy_working = []
        for btn in copy_btns[:3]:
            txt = await btn.inner_text()
            await btn.click()
            await p_docs.wait_for_timeout(200)
            txt_after = await btn.inner_text()
            copy_working.append((txt, txt_after))

        # Check search input if present
        doc_search = await p_docs.query_selector("input[type='search'], input[placeholder*='Search']")

        # ----------------------------------------------------
        # CONTACT PAGE
        # ----------------------------------------------------
        p_contact = await browser.new_page(viewport={"width": 1280, "height": 800})
        c_net = []
        p_contact.on("response", lambda r: c_net.append((r.status, r.url)))
        await p_contact.goto("https://verdischain.com/contact/", wait_until="networkidle")
        
        # Submit form
        await p_contact.select_option("#subject", index=1)
        await p_contact.fill("#name", "Auditor")
        await p_contact.fill("#email", "audit@test.com")
        await p_contact.fill("#message", "Testing contact form functionality.")
        await p_contact.click("button[type='submit']")
        await p_contact.wait_for_timeout(1000)
        
        contact_result = await p_contact.evaluate("""() => {
            const alert = document.querySelector('.alert, #formResult, #result, p.text-green-500, p.text-red-500, div[class*="success"], div[class*="error"]');
            return alert ? alert.innerText : 'No alert box';
        }""")

        # ----------------------------------------------------
        # API PAGE
        # ----------------------------------------------------
        p_api = await browser.new_page(viewport={"width": 1280, "height": 800})
        await p_api.goto("https://verdischain.com/api/", wait_until="networkidle")
        
        # Check mobile element causing overflow
        m_api = await browser.new_page(viewport={"width": 375, "height": 812})
        await m_api.goto("https://verdischain.com/api/")
        overflow_causes = await m_api.evaluate("""() => {
            const results = [];
            document.querySelectorAll('*').forEach(el => {
                if (el.scrollWidth > 375) {
                    results.push({
                        tag: el.tagName,
                        class: el.className,
                        id: el.id,
                        scrollWidth: el.scrollWidth,
                        text: el.innerText ? el.innerText.substring(0, 60).replace(/\\n/g, ' ') : ''
                    });
                }
            });
            return results;
        }""")

        # ----------------------------------------------------
        # TERMS & PRIVACY
        # ----------------------------------------------------
        p_terms = await browser.new_page(viewport={"width": 1280, "height": 800})
        await p_terms.goto("https://verdischain.com/terms/")
        terms_info = await p_terms.evaluate("() => document.body.innerText.substring(0, 500)")

        p_priv = await browser.new_page(viewport={"width": 1280, "height": 800})
        await p_priv.goto("https://verdischain.com/privacy/")
        priv_info = await p_priv.evaluate("() => document.body.innerText.substring(0, 500)")

        print("=== DETAILED FINDINGS ===")
        print("1. FAUCET:")
        print("  - Subresource 502:", [r for r in f_net if r[0] == 502])
        print("  - Faucet form alert:", faucet_alert)
        print("  - Mobile hamburger works:", nav_works)

        print("\n2. REFERRAL:")
        print("  - Copy button text before/after:", copy_text_before, "->", copy_text_after)
        print("  - Calc text:\n", calc_out['calcSectionText'])

        print("\n3. INCENTIVES:")
        print("  - Staking calc text:\n", inc_calc['boxText'])

        print("\n4. DOCS:")
        print("  - Code copy buttons tested:", copy_working)
        print("  - Search input present:", bool(doc_search))

        print("\n5. CONTACT:")
        print("  - Form submit result alert:", contact_result)
        print("  - Network calls during submit:", c_net)

        print("\n6. API:")
        print("  - Mobile overflow elements (>375px width):", len(overflow_causes))
        for oc in overflow_causes[:5]:
            print("    *", oc)

        await browser.close()

asyncio.run(run_detailed_analysis())
