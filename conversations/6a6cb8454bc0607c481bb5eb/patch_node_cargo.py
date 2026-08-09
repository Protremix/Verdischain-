import re

with open('/opt/verdis-chain-rust/node/Cargo.toml', 'r') as f:
    content = f.read()

# Add pallet-staking as optional dependency (right after frame-benchmarking-cli line)
old_cli = 'frame-benchmarking-cli = { version = "58.0.0", default-features = false, features = ["rocksdb"] }'
new_cli = old_cli + '\npallet-staking = { version = "49.0.0", default-features = false, optional = true }'
content = content.replace(old_cli, new_cli)

# Update runtime-benchmarks feature to enable pallet-staking
old_feature = 'runtime-benchmarks = ["verdis-runtime/runtime-benchmarks"]'
new_feature = 'runtime-benchmarks = ["verdis-runtime/runtime-benchmarks", "pallet-staking/runtime-benchmarks"]'
content = content.replace(old_feature, new_feature)

with open('/opt/verdis-chain-rust/node/Cargo.toml', 'w') as f:
    f.write(content)

print("Done")
