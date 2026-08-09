import random, time
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True, type_registry_preset=None)
keypair = Keypair.create_from_uri("//Bob")
print("Connected. Bob:", keypair.ss58_address)

remarks = [
    b"Bob validates on Verdis Chain",
    b"Staking VRDX for network security",
    b"Liquidity provided to AMM DEX",
    b"Carbon offset verified on-chain",
    b"Green validator scoring active",
    b"DPoS election in progress",
    b"VRDX token transfer completed",
    b"Decentralized exchange volume growing",
    b"Eco metrics updated on-chain",
    b"Reforestation project verified",
]

while True:
    try:
        remark = random.choice(remarks)
        call = substrate.compose_call("System", "remark", {"remark": remark})
        extrinsic = substrate.create_signed_extrinsic(call, keypair)
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=False)
        ts = time.strftime("%H:%M:%S")
        print("[" + ts + "] TX:", result.extrinsic_hash, "-", remark.decode(), flush=True)
    except Exception as e:
        ts = time.strftime("%H:%M:%S")
        print("[" + ts + "] Error:", str(e), flush=True)
    time.sleep(random.randint(7, 14))
