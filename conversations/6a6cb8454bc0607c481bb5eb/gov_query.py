import json, urllib.request, xxhash, struct, hashlib

def twox128(data):
    h1 = xxhash.xxh64(data, seed=0).intdigest()
    h2 = xxhash.xxh64(data, seed=1).intdigest()
    return h1.to_bytes(8, 'little') + h2.to_bytes(8, 'little')

def get_storage(pallet, item):
    key = '0x' + (twox128(pallet.encode()) + twox128(item.encode())).hex()
    req = urllib.request.Request('http://localhost:9933',
        data=json.dumps({'jsonrpc':'2.0','method':'state_getStorage','params':[key, None],'id':1}).encode(),
        headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    d = json.loads(resp.read())
    return d.get('result')

def decode_compact(raw, offset=0):
    b = raw[offset]
    if b & 0x03 == 0: return b >> 2, 1
    elif b & 0x03 == 1: return (b >> 2) | (raw[offset+1] << 6), 2
    elif b & 0x03 == 2: return (b >> 2) | (raw[offset+1] << 6) | (raw[offset+2] << 14) | (raw[offset+3] << 22), 4
    else:
        n = (b >> 2) + 4
        return int.from_bytes(raw[offset+1:offset+1+n], 'little'), 1 + n

def ss58_encode(pubkey, prefix=909):
    body = bytes([prefix]) + pubkey
    checksum = hashlib.blake2b(b'SS58PRE' + body, digest_size=64).digest()
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    num = int.from_bytes(body + checksum[:2], 'big')
    result = ''
    while num > 0:
        num, rem = divmod(num, 58)
        result = alphabet[rem] + result
    for b in body:
        if b == 0: result = '1' + result
        else: break
    return result

print('=== COUNCIL ===')
members_raw = get_storage('Council', 'Members')
if members_raw and members_raw != '0x':
    raw = bytes.fromhex(members_raw[2:])
    count, off = decode_compact(raw, 0)
    print(f'Members: {count}')
    for i in range(count):
        acct = raw[off:off+32]
        block_raw = raw[off+32:off+36]
        block = struct.unpack('<I', block_raw)[0] if len(block_raw) >= 4 else 0
        addr = ss58_encode(acct, 909)
        print(f'  {i+1}. {addr} (since block {block})')
        off += 36

prime_raw = get_storage('Council', 'Prime')
if prime_raw and prime_raw != '0x':
    raw = bytes.fromhex(prime_raw[2:])
    if raw[0] == 1 and len(raw) >= 33:
        print(f'Prime: {ss58_encode(raw[1:33], 909)}')

prop_count_raw = get_storage('Council', 'ProposalCount')
if prop_count_raw and prop_count_raw != '0x':
    raw = bytes.fromhex(prop_count_raw[2:])
    if len(raw) >= 4:
        print(f'ProposalCount: {struct.unpack("<I", raw[:4])[0]}')

print()
print('=== DEMOCRACY ===')
ref_count = get_storage('Democracy', 'ReferendumCount')
if ref_count and ref_count != '0x':
    raw = bytes.fromhex(ref_count[2:])
    if len(raw) >= 4:
        print(f'ReferendumCount: {struct.unpack("<I", raw[:4])[0]}')

for item in ['LaunchPeriod', 'VotingPeriod', 'EnactmentPeriod', 'CooloffPeriod']:
    val = get_storage('Democracy', item)
    if val and val != '0x':
        raw = bytes.fromhex(val[2:])
        if len(raw) >= 4:
            print(f'{item}: {struct.unpack("<I", raw[:4])[0]} blocks')

min_dep = get_storage('Democracy', 'MinimumDeposit')
if min_dep and min_dep != '0x':
    raw = bytes.fromhex(min_dep[2:])
    if len(raw) >= 16:
        print(f'MinimumDeposit: {int.from_bytes(raw[:16], "little") / 1e9} VRDX')

print()
print('=== TREASURY ===')
pot = get_storage('Treasury', 'Pot')
if pot and pot != '0x':
    raw = bytes.fromhex(pot[2:])
    if len(raw) >= 16:
        print(f'Pot: {int.from_bytes(raw[:16], "little") / 1e9} VRDX')
    else:
        print('Pot: 0 VRDX')
else:
    print('Pot: 0 VRDX')

for item in ['SpendPeriod', 'MaxApprovals', 'ProposalCount']:
    val = get_storage('Treasury', item)
    if val and val != '0x':
        raw = bytes.fromhex(val[2:])
        if len(raw) >= 4:
            print(f'{item}: {struct.unpack("<I", raw[:4])[0]}')

pbm = get_storage('Treasury', 'ProposalBondMinimum')
if pbm and pbm != '0x':
    raw = bytes.fromhex(pbm[2:])
    if len(raw) >= 16:
        print(f'ProposalBondMinimum: {int.from_bytes(raw[:16], "little") / 1e9} VRDX')
