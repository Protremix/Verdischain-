import random, time
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url='ws://127.0.0.1:9934', ss58_format=909, auto_discover=True, type_registry_preset=None)
keypair = Keypair.create_from_uri('//Alice')
print('Connected. Alice:', keypair.ss58_address)

remarks = [
    b'Verdis Chain: Building a greener blockchain',
    b'VRDX: 100B supply, 12B investor allocation',
    b'Carbon credits tracked on-chain',
    b'DPoS consensus with 21 validators',
    b'AMM DEX with 6 liquidity pools live',
    b'Eco-friendly blockchain with green scoring',
    b'Verdiscan: Real-time blockchain explorer',
    b'Green validators earning carbon credits',
    b'Testnet producing blocks with DPoS',
    b'Decentralized finance on Verdis Chain',
    b'Green validators securing the network',
    b'VRDX token powering the Verdis ecosystem',
    b'Block produced successfully on Verdis Chain',
    b'Substrate-based DPoS blockchain',
]

while True:
    try:
        remark = random.choice(remarks)
        call = substrate.compose_call('System', 'remark', {'remark': remark})
        extrinsic = substrate.create_signed_extrinsic(call, keypair)
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
        ts = time.strftime('%H:%M:%S')
        print('[' + ts + '] TX:', result.extrinsic_hash, '-', remark.decode(), flush=True)
    except Exception as e:
        ts = time.strftime('%H:%M:%S')
        print('[' + ts + '] Error:', str(e)[:120], flush=True)
    time.sleep(random.randint(3, 7))
