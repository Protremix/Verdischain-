import asyncio
import json
from playwright.async_api import async_playwright

async def run_audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Desktop context
        desktop_ctx = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        desktop_page = await desktop_ctx.new_page()
        
        console_logs = []
        network_requests = []
        network_responses = []
        
        desktop_page.on("console", lambda msg: console_logs.append({"type": msg.type, "text": msg.text}))
        
        def handle_request(req):
            network_requests.append({
                "url": req.url,
                "method": req.method,
                "resource_type": req.resource_type,
                "post_data": req.post_data
            })
            
        desktop_page.on("request", handle_request)
        
        async def handle_response(res):
            try:
                body = await res.text()
            except Exception:
                body = "<binary or failed>"
            network_responses.append({
                "url": res.url,
                "status": res.status,
                "headers": res.headers,
                "body": body[:2000] # truncate long bodies
            })
            
        desktop_page.on("response", handle_response)
        
        print("Navigating desktop...")
        response = await desktop_page.goto('https://verdischain.com/validators/', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2) # wait for any dynamic scripts
        
        await desktop_page.screenshot(path='desktop.png', full_page=True)
        
        desktop_html = await desktop_page.content()
        desktop_text = await desktop_page.inner_text('body')
        
        # Get validator rows/cards details
        # Check all tables, card lists, validator items
        validators_info = await desktop_page.evaluate('''() => {
            const result = [];
            // Try common selectors or generic list items / table rows
            const rows = document.querySelectorAll('tr, .validator-card, .validator-item, .card, [class*="validator"]');
            rows.forEach(r => {
                result.push({
                    tagName: r.tagName,
                    className: r.className,
                    innerText: r.innerText
                });
            });
            return result;
        }''')
        
        # Mobile context (375px)
        mobile_ctx = await browser.new_context(
            viewport={'width': 375, 'height': 812},
            is_mobile=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        )
        mobile_page = await mobile_ctx.new_page()
        
        print("Navigating mobile...")
        await mobile_page.goto('https://verdischain.com/validators/', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(2)
        await mobile_page.screenshot(path='mobile.png', full_page=True)
        
        # Check horizontal overflow on mobile
        overflow_info = await mobile_page.evaluate('''() => {
            const body = document.body;
            const html = document.documentElement;
            const documentWidth = Math.max(body.scrollWidth, body.offsetWidth, html.clientWidth, html.scrollWidth, html.offsetWidth);
            const viewportWidth = window.innerWidth;
            
            // Find elements extending past viewport
            const overflowingElements = [];
            document.querySelectorAll('*').forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.right > viewportWidth + 1) {
                    overflowingElements.append ? overflowingElements.append(el.tagName + '.' + el.className) : overflowingElements.push(el.tagName + '.' + el.className + ' (right: ' + rect.right + ')');
                }
            });
            
            return {
                documentWidth,
                viewportWidth,
                hasHorizontalScroll: documentWidth > viewportWidth,
                overflowingElements: overflowingElements.slice(0, 20)
            };
        }''')
        
        # Save output
        data = {
            "console_logs": console_logs,
            "network_requests": network_requests,
            "network_responses": network_responses,
            "desktop_text": desktop_text,
            "validators_info": validators_info,
            "mobile_overflow": overflow_info
        }
        
        with open("audit_results.json", "w") as f:
            json.dump(data, f, indent=2)
            
        print("Audit done!")
        await browser.close()

asyncio.run(run_audit())
