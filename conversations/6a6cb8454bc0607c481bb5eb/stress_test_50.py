#!/usr/bin/env python3
"""
Verdis Chain 50-Transfer Stress Test
Moves VRDX between 5 wallets back and forth 50 times.
"""
import time, sys, traceback
from substrateinterface import SubstrateInterface, Keypair

print("=" * 60)
print("VERDIS CHAIN — 50-TRANSFER STRESS TEST")
print("=" * 60)

# Connect to node
substrate = SubstrateInterface(
    url='ws://127.0.0.1:9933',
    ss58_format=909,
    auto_discover=True,
    type_registry_preset=None
)
print(f"Connected to Verdis Chain at block #{substrate.get_block_header()['header']['number']}")

# Create keypairs
wallets = {}
for name in ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']:
    wallets[name] = Keypair.create_from_uri(f'//{name}')
    addr = wallets[name].ss58_address
    # Get balance
    try:
        result = substrate.query('System', 'Account', [addr])
        free = result.value.get('data', {}).get('free', 0)
        print(f"  {name}: {addr} — Balance: {free/1e9:.4f} VRDX")
    except Exception as e:
        print(f"  {name}: {addr} — Balance query error: {e}")

print()
TRANSFER_AMOUNT = 1000000000  # 1 VRDX (9 decimals)

# 50 transfers: cycle through wallet pairs
pairs = [
    ('Alice', 'Bob'),
    ('Bob', 'Charlie'),
    ('Charlie', 'Dave'),
    ('Dave', 'Eve'),
    ('Eve', 'Alice'),
]

success = 0
failed = 0
errors = []
start_block = substrate.get_block_header()['header']['number']

print(f"Starting 50 transfers (1 VRDX each)...")
print("-" * 60)

for i in range(50):
    sender_name, receiver_name = pairs[i % len(pairs)]
    sender = wallets[sender_name]
    receiver_addr = wallets[receiver_name].ss58_address
    
    try:
        # Compose and sign transfer
        call = substrate.compose_call(
            'Balances',
            'transfer_allow_death',
            {
                'dest': {'Id': receiver_addr},
                'value': TRANSFER_AMOUNT
            }
        )
        extrinsic = substrate.create_signed_extrinsic(call, sender)
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
        
        if result.is_success:
            success += 1
            block_num = substrate.get_block_header()['header']['number']
            print(f"  [{i+1:2d}/50] {sender_name}→{receiver_name}: ✅ Block #{block_num} hash={result.extrinsic_hash[:16]}...")
        else:
            failed += 1
            err = f"[{i+1:2d}/50] {sender_name}→{receiver_name}: ❌ {result.error_message}"
            errors.append(err)
            print(err)
            
    except Exception as e:
        failed += 1
        err = f"[{i+1:2d}/50] {sender_name}→{receiver_name}: ❌ {str(e)[:80]}"
        errors.append(err)
        print(err)
    
    # Small delay between transfers
    time.sleep(0.5)

end_block = substrate.get_block_header()['header']['number']
blocks_produced = end_block - start_block

print("-" * 60)
print(f"RESULTS:")
print(f"  Total: {success + failed}")
print(f"  Success: {success}")
print(f"  Failed: {failed}")
print(f"  Success rate: {success/(success+failed)*100:.1f}%")
print(f"  Blocks produced during test: {blocks_produced}")
print(f"  Start block: #{start_block}")
print(f"  End block: #{end_block}")

# Final balance check
print()
print("FINAL BALANCES:")
for name, kp in wallets.items():
    try:
        result = substrate.query('System', 'Account', [kp.ss58_address])
        free = result.value.get('data', {}).get('free', 0)
        print(f"  {name}: {free/1e9:.4f} VRDX")
    except Exception as e:
        print(f"  {name}: Error: {e}")

if errors:
    print()
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  {e}")

print()
print("=" * 60)
if success == 50:
    print("✅ ALL 50 TRANSFERS SUCCESSFUL")
else:
    print(f"⚠️  {failed} TRANSFERS FAILED OUT OF 50")
print("=" * 60)
