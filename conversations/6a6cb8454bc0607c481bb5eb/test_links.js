const { chromium } = require('playwright');
const fs = require('fs');
const https = require('https');
const http = require('http');
const { URL } = require('url');

const pages = ['eco', 'validators', 'incentives', 'referral'];

function checkUrl(urlStr) {
  return new Promise((resolve) => {
    if (!urlStr || urlStr.startsWith('javascript:') || urlStr === '#') {
      return resolve({ url: urlStr, status: 'JAVASCRIPT_OR_HASH', ok: false });
    }
    try {
      const u = new URL(urlStr);
      const client = u.protocol === 'https:' ? https : http;
      const req = client.request(u, { method: 'HEAD', timeout: 5000 }, (res) => {
        resolve({ url: urlStr, status: res.statusCode, ok: res.statusCode >= 200 && res.statusCode < 400 });
      });
      req.on('error', (e) => {
        // Retry with GET
        const reqGet = client.request(u, { method: 'GET', timeout: 5000 }, (res2) => {
          resolve({ url: urlStr, status: res2.statusCode, ok: res2.statusCode >= 200 && res2.statusCode < 400 });
        });
        reqGet.on('error', (e2) => {
          resolve({ url: urlStr, status: 'ERROR: ' + e2.message, ok: false });
        });
        reqGet.end();
      });
      req.end();
    } catch (e) {
      resolve({ url: urlStr, status: 'INVALID_URL', ok: false });
    }
  });
}

async function run() {
  const allLinksReport = {};

  for (const pageName of pages) {
    const links = JSON.parse(fs.readFileSync(`links_${pageName}.json`));
    console.log(`Checking ${links.length} links for ${pageName}...`);
    const results = [];
    for (const link of links) {
      const res = await checkUrl(link.href);
      results.push({
        location: link.location,
        text: link.text,
        href: link.href,
        rawHref: link.rawHref,
        status: res.status,
        ok: res.ok
      });
    }
    allLinksReport[pageName] = results;
  }

  fs.writeFileSync('links_report.json', JSON.stringify(allLinksReport, null, 2));
  console.log('Link check done!');
}

run();
