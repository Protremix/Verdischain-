#!/usr/bin/env python3
"""Fix faucet page: remove fake data, add API fetch for real distributions."""
import re

with open('/var/www/verdiscan/faucet/index.html', 'r') as f:
    content = f.read()

# 1. Fix fake fallback values
# "faucetStats.totalDispensed || 2450000" -> "faucetStats.totalDispensed || 0"
content = content.replace('2450000', '0')
# "faucetStats.todayRequests || 95" -> "faucetStats.todayRequests || 0"
content = content.replace('faucetStats.todayRequests || 95', 'faucetStats.todayRequests || 0')

# 2. Replace hardcoded distributions array with empty array + API fetch
# Find the hardcoded distributions array
old_distributions = """// Recent distributionsconst distributions = [{ addr: 'kibKmJuKipPp71a51bDYpwUhChYgF5Kzmtm8Q67b45EWW77gD', token: 'VRDX', amount: 100, hash: '0x1a2b3c...', time: '2m ago' },{ addr: 'kibL4Atq5fi7EboD6fWiLMY4ES6Ry9K3K2Gj8KxYqS9rZGfJ', token: 'cVRDX', amount: 50, hash: '0x4d5e6f...', time: '5m ago' },{ addr: 'kib7yq5N3vG8mO1bR7qXpW2vF4jH6tE3wZ9sL8kR1mN4cVpC', token: 'VRDX', amount: 100, hash: '0x7g8h9i...', time: '12m ago' },{ addr: 'kibE5QzsU4tGZGEHTeYDyJAKdykzdaoEDkNpQ39ye7o2XaWzU', token: 'VRDX', amount: 100, hash: '0x0j1k2l...', time: '18m ago' },{ addr: 'kiZev8vhKwAGf7DnxDcG2YpQfsuyk8FptFYg4ynqy3p7HoeGWvF', token: 'cVRDX', amount: 50, hash: '0x3m4n5o...', time: '25m ago' },{ addr: 'kiZhaD6qNGAAHjqCckPrMYUrxi3f87ZhjgKwQWo95LDHp6qiH', token: 'VRDX', amount: 100, hash: '0x6p7q8r...', time: '38m ago' },];"""

new_distributions = """// Recent distributions - loaded from faucet API
let distributions = [];"""

content = content.replace(old_distributions, new_distributions)

# 3. Add API fetch for real distribution data after renderHistory() call
old_init = "generateCaptcha();\nrenderHistory();"
new_init = """generateCaptcha();
renderHistory();

// Fetch real distribution data from faucet API
async function loadDistributions() {
  try {
    const res = await fetch('/faucet/api/stats');
    if (res.ok) {
      const data = await res.json();
      if (data.distributions && data.distributions.length > 0) {
        distributions = data.distributions.map(d => ({
          addr: d.address || 'Unknown',
          token: 'VRDX',
          amount: d.amount || 0,
          hash: (d.txHash || 'pending').toString().slice(0, 20),
          time: formatTimeAgo(d.time)
        }));
        renderHistory();
      }
    }
  } catch(e) {
    console.error('Failed to load faucet distributions:', e);
  }
}
function formatTimeAgo(isoTime) {
  if (!isoTime) return 'unknown';
  const diff = Date.now() - new Date(isoTime).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return mins + 'm ago';
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return hrs + 'h ago';
  return Math.floor(hrs / 24) + 'd ago';
}
loadDistributions();"""

content = content.replace(old_init, new_init)

with open('/var/www/verdiscan/faucet/index.html', 'w') as f:
    f.write(content)
print(f'Faucet page fixed: removed fake data, added API fetch ({len(content)} bytes)')
