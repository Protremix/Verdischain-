#!/usr/bin/env python3
"""Migrate all VCO references to VRS in the persisted state file"""
import json
import re

STATE_FILE = "/opt/verdis/blobs/verdis-state.json"

with open(STATE_FILE, 'r') as f:
    state = json.load(f)

# Track changes
changes = 0

# 1. Migrate pool names (tokenA/tokenB)
for pool in state.get('pools', []):
    if pool.get('tokenA') == 'VCO':
        pool['tokenA'] = 'VRS'
        changes += 1
    if pool.get('tokenB') == 'VCO':
        pool['tokenB'] = 'VRS'
        changes += 1
    if pool.get('id', '').startswith('VCO/') or pool.get('id', '').startswith('VCO-'):
        pool['id'] = pool['id'].replace('VCO', 'VRS')
        changes += 1
    if '/VCO' in pool.get('id', ''):
        pool['id'] = pool['id'].replace('/VCO', '/VRS')
        changes += 1
    if 'VCO/' in pool.get('id', ''):
        pool['id'] = pool['id'].replace('VCO/', 'VRS/')
        changes += 1

# 2. Migrate market data (token references)
market = state.get('marketData', {})
if market:
    # Price history
    for ph in market.get('priceHistory', []):
        for pair in ph.get('prices', []):
            if isinstance(pair, dict):
                if pair.get('token') == 'VCO':
                    pair['token'] = 'VRS'
                    changes += 1
    # Swap history
    for swap in market.get('swapHistory', []):
        if swap.get('tokenIn') == 'VCO':
            swap['tokenIn'] = 'VRS'
            changes += 1
        if swap.get('tokenOut') == 'VCO':
            swap['tokenOut'] = 'VRS'
            changes += 1
    # Price points
    for pp in market.get('pricePoints', []):
        if pp.get('pair', '').startswith('VCO/') or pp.get('pair', '').endswith('/VCO'):
            pp['pair'] = pp['pair'].replace('VCO', 'VRS')
            changes += 1
    # Token info
    tokens = market.get('tokens', {})
    if 'VCO' in tokens:
        tokens['VRS'] = tokens.pop('VCO')
        changes += 1

# 3. Do a final raw string replacement for any remaining VCO references
text = json.dumps(state)
before = text.count('VCO')
text = text.replace('"VCO"', '"VRS"')
text = text.replace('VCO/', 'VRS/')
text = text.replace('/VCO', '/VRS')
after = text.count('VCO')
changes += (before - after)

state = json.loads(text)

with open(STATE_FILE, 'w') as f:
    json.dump(state, f)

# Verify
with open(STATE_FILE, 'r') as f:
    verify = json.load(f)

vco_remaining = json.dumps(verify).count('VCO')
print(f"Migration complete: {changes} fields changed, {vco_remaining} VCO references remaining")
print("\nMigrated pools:")
for p in verify.get('pools', []):
    print(f"  {p.get('tokenA','?')}/{p.get('tokenB','?')} | A: {p.get('reserveA',0):.0f} | B: {p.get('reserveB',0):.0f}")
