const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const urls = [
  { name: 'eco', url: 'https://verdischain.com/eco/?nocache=50009' },
  { name: 'validators', url: 'https://verdischain.com/validators/?nocache=50010' },
  { name: 'incentives', url: 'https://verdischain.com/incentives/?nocache=50011' },
  { name: 'referral', url: 'https://verdischain.com/referral/?nocache=50012' }
];

async function audit() {
  const browser = await chromium.launch({ headless: true });

  for (const item of urls) {
    console.log(`=== AUDITING ${item.name} (${item.url}) ===`);
    const context = await browser.newContext({
      viewport: { width: 1440, height: 900 }
    });
    const page = await context.newPage();

    const consoleLogs = [];
    const pageErrors = [];
    const failedRequests = [];
    const networkRequests = [];

    page.on('console', msg => consoleLogs.push({ type: msg.type(), text: msg.text() }));
    page.on('pageerror', err => pageErrors.push(err.toString()));
    page.on('requestfailed', req => failedRequests.push({ url: req.url(), failure: req.failure() }));
    page.on('request', req => networkRequests.push(req.url()));

    await page.goto(item.url, { waitUntil: 'networkidle', timeout: 30000 }).catch(e => console.log('Goto error:', e));

    // Wait 3 seconds for any dynamic JS to render
    await page.waitForTimeout(3000);

    // Take screenshot
    const screenshotPath = `screenshot_${item.name}.png`;
    await page.screenshot({ path: screenshotPath, fullPage: true });

    // Extract HTML content
    const html = await page.content();
    fs.writeFileSync(`page_${item.name}.html`, html);

    // Extract innerText
    const visibleText = await page.evaluate(() => document.body.innerText);
    fs.writeFileSync(`text_${item.name}.txt`, visibleText);

    // Extract scripts / inline code / JS variables
    const scripts = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('script')).map(s => ({
        src: s.src,
        text: s.innerText
      }));
    });
    fs.writeFileSync(`scripts_${item.name}.json`, JSON.stringify(scripts, null, 2));

    // Extract all links
    const links = await page.evaluate(() => {
      const anchors = Array.from(document.querySelectorAll('a'));
      return anchors.map(a => ({
        text: a.innerText.trim(),
        href: a.href,
        rawHref: a.getAttribute('href'),
        outerHTML: a.outerHTML,
        location: a.closest('nav') ? 'nav' : (a.closest('footer') ? 'footer' : 'body')
      }));
    });
    fs.writeFileSync(`links_${item.name}.json`, JSON.stringify(links, null, 2));

    // Check overlapping elements & layout overflow
    const layoutIssues = await page.evaluate(() => {
      const issues = [];
      const allElems = Array.from(document.querySelectorAll('body *'));

      // Check text container overflows or offscreen
      allElems.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
          if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflowX !== 'hidden' && getComputedStyle(el).overflowX !== 'scroll' && getComputedStyle(el).overflowX !== 'auto') {
            // potential overflow issue
            issues.push({
              type: 'horizontal_overflow',
              tag: el.tagName,
              id: el.id,
              class: el.className,
              scrollWidth: el.scrollWidth,
              clientWidth: el.clientWidth,
              text: el.innerText ? el.innerText.substring(0, 50) : ''
            });
          }
        }
      });

      return issues;
    });

    console.log(`Logs: ${consoleLogs.length}, PageErrors: ${pageErrors.length}, FailedReqs: ${failedRequests.length}`);

    fs.writeFileSync(`audit_data_${item.name}.json`, JSON.stringify({
      consoleLogs,
      pageErrors,
      failedRequests,
      networkRequests,
      layoutIssues
    }, null, 2));

    await context.close();
  }

  await browser.close();
}

audit().catch(console.error);
