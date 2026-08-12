#!/usr/bin/env python3
"""Add impl WeightInfo for () to turbine, sealevel, ibc weights.rs and fix test configs"""

fixes = []

# Fix turbine
with open('/opt/verdis-chain-rust/pallets/turbine/src/weights.rs') as f:
    content = f.read()
# Add impl WeightInfo for () at the end
if 'impl WeightInfo for ()' not in content:
    content += '''
impl WeightInfo for () {
    fn register_shard() -> Weight { Weight::from_parts(10_000, 0) }
    fn rebuild_tree(_v: u32) -> Weight { Weight::from_parts(10_000, 0) }
    fn mark_block_propagated() -> Weight { Weight::from_parts(10_000, 0) }
}
'''
    with open('/opt/verdis-chain-rust/pallets/turbine/src/weights.rs', 'w') as f:
        f.write(content)
    fixes.append('turbine weights.rs - added impl ()')

# Fix sealevel
with open('/opt/verdis-chain-rust/pallets/sealevel/src/weights.rs') as f:
    content = f.read()
if 'impl WeightInfo for ()' not in content:
    content += '''
impl WeightInfo for () {
    fn create_batch() -> Weight { Weight::from_parts(10_000, 0) }
    fn report_execution() -> Weight { Weight::from_parts(10_000, 0) }
    fn report_conflict() -> Weight { Weight::from_parts(10_000, 0) }
}
'''
    with open('/opt/verdis-chain-rust/pallets/sealevel/src/weights.rs', 'w') as f:
        f.write(content)
    fixes.append('sealevel weights.rs - added impl ()')

# Fix ibc
with open('/opt/verdis-chain-rust/pallets/ibc/src/weights.rs') as f:
    content = f.read()
if 'impl WeightInfo for ()' not in content:
    content += '''
impl WeightInfo for () {
    fn create_client() -> Weight { Weight::from_parts(10_000, 0) }
    fn open_connection() -> Weight { Weight::from_parts(10_000, 0) }
    fn open_channel() -> Weight { Weight::from_parts(10_000, 0) }
    fn send_packet() -> Weight { Weight::from_parts(10_000, 0) }
    fn recv_packet() -> Weight { Weight::from_parts(10_000, 0) }
    fn acknowledge_packet() -> Weight { Weight::from_parts(10_000, 0) }
    fn timeout_packet() -> Weight { Weight::from_parts(10_000, 0) }
    fn transfer() -> Weight { Weight::from_parts(10_000, 0) }
    fn close_channel() -> Weight { Weight::from_parts(10_000, 0) }
    fn update_client() -> Weight { Weight::from_parts(10_000, 0) }
}
'''
    with open('/opt/verdis-chain-rust/pallets/ibc/src/weights.rs', 'w') as f:
        f.write(content)
    fixes.append('ibc weights.rs - added impl ()')

# Now fix the test files to add type WeightInfo = ();
for pallet in ['turbine', 'sealevel', 'poh', 'ibc']:
    fpath = f'/opt/verdis-chain-rust/pallets/{pallet}/src/tests.rs'
    with open(fpath) as f:
        content = f.read()
    
    if 'type WeightInfo' not in content:
        # Find the impl Config for Test block and add WeightInfo
        # Pattern: "impl Config for Test {" or "impl Config for Test {}"
        if 'impl Config for Test {}' in content:
            content = content.replace(
                'impl Config for Test {}',
                'impl Config for Test {\n    type WeightInfo = ();\n}',
                1
            )
            with open(fpath, 'w') as f:
                f.write(content)
            fixes.append(f'{pallet} tests.rs - added type WeightInfo = ()')
        elif 'impl Config for Test {' in content:
            content = content.replace(
                'impl Config for Test {',
                'impl Config for Test {\n    type WeightInfo = ();',
                1
            )
            with open(fpath, 'w') as f:
                f.write(content)
            fixes.append(f'{pallet} tests.rs - added type WeightInfo = ()')
        else:
            fixes.append(f'{pallet} tests.rs - COULD NOT FIND impl Config for Test')
    else:
        fixes.append(f'{pallet} tests.rs - already has WeightInfo')

for f in fixes:
    print(f)
