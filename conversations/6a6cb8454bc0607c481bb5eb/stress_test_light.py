#!/usr/bin/env python3
"""
Verdis Chain Lightweight Transfer Test (10 transfers, not 50)
Designed to NOT crash the server.
"""
import time, sys
from substrateinterface import SubstrateInterface, Keypair

print("=" * 50)
print("VERDIS CHAIN — 10-TRANSFER TEST")
print("=" * 50)

substrate = SubstrateInterface(
    url='ws://127.0.0.1:9933',
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)

hdr = substrate.get_block_header()
block_num = hdr['header']['number'] if 'header' in hdr else hdr.get('number', 0)
print(f"Connected at block #{block_num}")

wallets = {}
for name in ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']:
    wallets[name] = Keypair.create_from_uri(f'//{name}')

# Print initial balances
print("\nInitial balances:")
for name, kp in wallets.items():
    try:
        result = substrate.query('System', 'Account', [kp.ss58_address])
        free = result.value.get('data', {}).get('free', 0)
        print(f"  {name}: {free/1e9:.4f} VRDX")
    except:
        print(f"  {name}: query error")

TRANSFER_AMOUNT = 1000000000  # 1 VRDX
pairs = [('Alice', 'Bob'), ('Bob', 'Charlie'), ('Charlie', 'Dave'), ('Dave', 'Eve'), ('Eve', 'Alice')]

success = 0
failed = 0

print(f"\nStarting 10 transfers (1 VRDX each, 2s delay)...")
print("-" * 50)

for i in range(10):
    sender_name, receiver_name = pairs[i % len(pairs)]
    sender = wallets[sender_name]
    receiver_addr = wallets[receiver_name].ss58_address
    
    try:
        call = substrate.compose_call(
            'Balances',
            'transfer_allow_death',
            {'dest': {'Id': receiver_addr}, 'value': TRANSFER_AMOUNT}
        )
        extrinsic = substrate.create_signed_extrinsic(call, sender)
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
        
        if result.is_success:
            success += 1
            print(f"  [{i+1:2d}/10] {sender_name}→{receiver_name}: OK hash={result.extrinsic_hash[:16]}...")
        else:
            failed += 1
            print(f"  [{i+1:2d}/10] {sender_name}→{receiver_name}: FAIL {result.error_message}")
    except Exception as e:
        failed += 1
        print(f"  [{i+1:2d}/10] {sender_name}→{receiver_name}: ERROR {str(e)[:60]}")
    
    time.sleep(2)  # Gentle delay

print("-" * 50)
print(f"Success: {success}/10 ({success*10}%)")
print(f"Failed: {failed}/10")

# Final balances
print("\nFinal balances:")
for name, kp in wallets.items():
    try:
        result = substrate.query('System', 'Account', [kp.ss58_address])
        free = result.value.get('data', {}).get('free', 0)
        print(f"  {name}: {free/1e9:.4f} VRDX")
    except:
        print(f"  {name}: query error")

if success == 10:
    print("\n✅ ALL 10 TRANSFERS SUCCESSFUL")
else:
    print(f"\n⚠️ {failed} FAILED")
