#!/usr/bin/env python3
from substrateinterface import SubstrateInterface, Keypair

substrate = SubstrateInterface(url="http://127.0.0.1:9933", ss58_format=909, auto_discover=True)
for name in ["//Alice", "//Bob", "//Charlie", "//Dave", "//Eve", "//Ferdie"]:
    kp = Keypair.create_from_uri(name)
    r = substrate.query("System", "Account", [kp.ss58_address])
    bal = r.value.get("data", {}).get("free", 0) if r else 0
    print(f"{name} ({kp.ss58_address}): {bal/10**9:.2f} VRDX")
