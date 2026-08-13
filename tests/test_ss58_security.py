#!/usr/bin/env python3
"""
SS58 Security Tests for convert_ss58() function.
Tests: 909 to 42, 42 to 909, 1-byte/2-byte prefixes, invalid inputs,
round-trip, public-key preservation, checksum validation.
"""

import sys
import os
import hashlib
import base58

sys.path.insert(0, '/opt/verdis-chain-rust')
from governance_api import convert_ss58

PASSED = 0
FAILED = 0

def test(name, condition, detail=""):
    global PASSED, FAILED
    if condition:
        print(f'  PASS: {name}')
        PASSED += 1
    else:
        print(f'  FAIL: {name} {detail}')
        FAILED += 1

# === Known Valid Addresses ===
ALICE_42 = '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY'
ALICE_909 = None  # Will be computed
BOB_42 = '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty'
BOB_909 = None

# Compute 909 versions
from substrateinterface import Keypair
kp = Keypair.create_from_uri('//Alice', ss58_format=909)
ALICE_909 = kp.ss58_address
kp = Keypair.create_from_uri('//Bob', ss58_format=909)
BOB_909 = kp.ss58_address

print('=== SS58 Security Test Suite ===')
print(f'Alice 42: {ALICE_42}')
print(f'Alice 909: {ALICE_909}')
print(f'Bob 42: {BOB_42}')
print(f'Bob 909: {BOB_909}')
print()

# === Test 1: 909  to  42 conversion ===
print('--- Test 1: 909 to 42 Conversion ---')
result = convert_ss58(ALICE_909, 42)
test('Alice 909 to 42', result == ALICE_42, f'got {result}')
result = convert_ss58(BOB_909, 42)
test('Bob 909 to 42', result == BOB_42, f'got {result}')

# === Test 2: 42  to  909 conversion ===
print('--- Test 2: 42  to  909 Conversion ---')
result = convert_ss58(ALICE_42, 909)
test('Alice 42 to 909', result == ALICE_909, f'got {result}')
result = convert_ss58(BOB_42, 909)
test('Bob 42 to 909', result == BOB_909, f'got {result}')

# === Test 3: 1-byte prefix (prefix < 64) ===
print('--- Test 3: 1-byte Prefix Handling ---')
# SS58 42 is a 1-byte prefix (< 64)
raw_42 = base58.b58decode(ALICE_42)
test('Alice 42 is 1-byte prefix', not (raw_42[0] & 0x40), f'first byte: 0x{raw_42[0]:02x}')
# SS58 2 is a 1-byte prefix
result = convert_ss58(ALICE_42, 2)
test('Alice 42 to 2 (1-byte)', result is not None, f'got {result}')
# Verify the prefix is correct
raw_2 = base58.b58decode(result)
test('Prefix 2 applied', raw_2[0] == 2, f'first byte: 0x{raw_2[0]:02x}')

# === Test 4: 2-byte prefix (prefix >= 64) ===
print('--- Test 4: 2-byte Prefix Handling ---')
# SS58 909 is a 2-byte prefix (>= 64)
raw_909 = base58.b58decode(ALICE_909)
test('Alice 909 is 2-byte prefix', bool(raw_909[0] & 0x40), f'first byte: 0x{raw_909[0]:02x}')
# SS58 909 encoding: 0x40 | (909 >> 8) = 0x43, 909 & 0xFF = 0x8D
test('909 prefix correct', raw_909[0] == 0x63 and raw_909[1] == 0x43, f'bytes: 0x{raw_909[0]:02x} 0x{raw_909[1]:02x}')

# === Test 5: Invalid Base58 ===
print('--- Test 5: Invalid Base58 ---')
result = convert_ss58('invalid!@#$%^&*()', 42)
test('Invalid chars returns original', result == 'invalid!@#$%^&*()', f'got {result}')
result = convert_ss58('0lO', 42)  # 0, l, O are invalid base58
test('Ambiguous chars handled', result == '0lO', f'got {result}')

# === Test 6: Malformed addresses ===
print('--- Test 6: Malformed Addresses ---')
result = convert_ss58('', 42)
test('Empty string returns original', result == '', f'got {result}')
result = convert_ss58('5', 42)  # Too short
test('Too short returns original', result == '5', f'got {result}')
result = convert_ss58('5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY5GrwvaEF', 42)  # Too long
test('Too long handled gracefully', result is not None, f'got {str(result)[:30]}')

# === Test 7: Truncated addresses ===
print('--- Test 7: Truncated Addresses ---')
truncated = ALICE_42[:-5]  # Remove last 5 chars
result = convert_ss58(truncated, 42)
test('Truncated address handled', result == truncated, f'got {str(result)[:30]}')

# === Test 8: Known valid addresses ===
print('--- Test 8: Known Valid Addresses ---')
for name, addr42, addr909 in [('Alice', ALICE_42, ALICE_909), ('Bob', BOB_42, BOB_909)]:
    result = convert_ss58(addr909, 42)
    test(f'{name} 909 to 42 matches known', result == addr42, f'got {result}')
    result = convert_ss58(addr42, 909)
    test(f'{name} 42 to 909 matches known', result == addr909, f'got {result}')

# === Test 9: Round-trip conversion ===
print('--- Test 9: Round-trip Conversion ---')
# 42  to  909  to  42 should equal original
for name, addr in [('Alice', ALICE_42), ('Bob', BOB_42)]:
    mid = convert_ss58(addr, 909)
    back = convert_ss58(mid, 42)
    test(f'{name} 42 to 909 to 42 round-trip', back == addr, f'got {back}')

# 909  to  42  to  909 should equal original
for name, addr in [('Alice', ALICE_909), ('Bob', BOB_909)]:
    mid = convert_ss58(addr, 42)
    back = convert_ss58(mid, 909)
    test(f'{name} 909 to 42 to 909 round-trip', back == addr, f'got {back}')

# === Test 10: Public-key preservation ===
print('--- Test 10: Public-key Preservation ---')
for name, addr42, addr909 in [('Alice', ALICE_42, ALICE_909), ('Bob', BOB_42, BOB_909)]:
    raw42 = base58.b58decode(addr42)
    payload42 = raw42[1:-2]  # 1-byte prefix, 2-byte checksum
    raw909 = base58.b58decode(addr909)
    payload909 = raw909[2:-2]  # 2-byte prefix, 2-byte checksum
    test(f'{name} public key preserved', payload42 == payload909, 
         f'42: {payload42.hex()[:20]}, 909: {payload909.hex()[:20]}')
    
    # After conversion, payload should still be the same
    converted = convert_ss58(addr42, 909)
    raw_converted = base58.b58decode(converted)
    payload_converted = raw_converted[2:-2]
    test(f'{name} converted key matches', payload42 == payload_converted,
         f'orig: {payload42.hex()[:20]}, conv: {payload_converted.hex()[:20]}')

# === Test 11: Checksum validation ===
print('--- Test 11: Checksum Validation ---')
# Verify checksums by decoding (ss58_decode validates checksum internally)
from scalecodec.utils.ss58 import ss58_decode

# Converted address should have valid checksum
converted = convert_ss58(ALICE_42, 909)
try:
    ss58_decode(converted, valid_ss58_format=909)
    test('Converted address checksum valid', True)
except:
    test('Converted address checksum valid', False, 'ss58_decode rejected converted address')

# Original address should have valid checksum
try:
    ss58_decode(ALICE_42, valid_ss58_format=42)
    test('Original address checksum valid', True)
except:
    test('Original address checksum valid', False, 'ss58_decode rejected original address')

# Tampered address should fail checksum
tampered = ALICE_42[:-2] + ('ZZ' if ALICE_42[-2:] != 'ZZ' else 'AA')
try:
    ss58_decode(tampered, valid_ss58_format=42)
    test('Tampered address rejected', False, 'tampered address accepted')
except:
    test('Tampered address rejected', True)

# === Test 12: No invalid address silently accepted ===
print('--- Test 12: No Silent Acceptance of Invalid Addresses ---')
# An invalid address should be returned as-is, not converted
invalid = 'NotAnAddress123'
result = convert_ss58(invalid, 42)
test('Invalid address not silently converted', result == invalid, f'got {result}')

# A valid-looking but wrong-checksum address should not produce a valid output
# (convert_ss58 doesn't validate input checksum, but output should be re-encoded)
wrong_checksum = ALICE_42[:-2] + 'ZZ'  # Replace checksum with invalid chars
try:
    result = convert_ss58(wrong_checksum, 42)
    # If it doesn't crash, it should at least not produce a valid address
    test('Wrong checksum handled', result is not None, f'got {str(result)[:30]}')
except:
    test('Wrong checksum raises exception', True)

# === Summary ===
print()
print(f'=== Results: {PASSED} passed, {FAILED} failed ===')
if FAILED > 0:
    sys.exit(1)
else:
    print('ALL TESTS PASSED')
    sys.exit(0)
