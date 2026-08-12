#!/usr/bin/env python3
"""Patch faucet_py.py to add auto-reconnect on stale WebSocket connection."""

with open('/opt/verdis-chain-rust/faucet_py.py', 'r') as f:
    content = f.read()

old_send_drip = '''def send_drip(dest_address):
    with lock:
        try:
            call = substrate.compose_call(
                call_module='Balances',
                call_function='transfer_allow_death',
                call_params={'dest': dest_address, 'value': AMOUNT_PLANCK}
            )
            extrinsic = substrate.create_signed_extrinsic(call=call, keypair=faucet_kp)
            tx_hash = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False)
            return True, "0x" + extrinsic.extrinsic_hash.hex()
        except Exception as e:
            return False, str(e)'''

new_send_drip = '''def reconnect():
    global substrate
    try:
        substrate = SubstrateInterface(url=NODE_URL, ss58_format=SS58_FORMAT, auto_discover=True, type_registry_preset=None)
        print(f'[{time.strftime("%H:%M:%S")}] Reconnected to node')
        return True
    except Exception as e:
        print(f'[{time.strftime("%H:%M:%S")}] Reconnect failed: {e}')
        return False

def _attempt_drip(dest_address):
    call = substrate.compose_call(
        call_module='Balances',
        call_function='transfer_allow_death',
        call_params={'dest': dest_address, 'value': AMOUNT_PLANCK}
    )
    extrinsic = substrate.create_signed_extrinsic(call=call, keypair=faucet_kp)
    tx_hash = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False)
    return "0x" + extrinsic.extrinsic_hash.hex()

def send_drip(dest_address):
    with lock:
        try:
            tx_hash = _attempt_drip(dest_address)
            return True, tx_hash
        except Exception as e:
            err = str(e)
            reconnect_triggers = ('broken pipe', 'connection', 'websocket', 'closed', 'timeout')
            if any(t in err.lower() for t in reconnect_triggers):
                print(f'[{time.strftime("%H:%M:%S")}] Connection error ({err}), reconnecting...')
                if reconnect():
                    try:
                        tx_hash = _attempt_drip(dest_address)
                        return True, tx_hash
                    except Exception as e2:
                        return False, str(e2)
            return False, err'''

if old_send_drip not in content:
    print("PATCH FAILED: old_send_drip pattern not found")
else:
    content = content.replace(old_send_drip, new_send_drip)
    with open('/opt/verdis-chain-rust/faucet_py.py', 'w') as f:
        f.write(content)
    print("PATCH APPLIED SUCCESSFULLY")
