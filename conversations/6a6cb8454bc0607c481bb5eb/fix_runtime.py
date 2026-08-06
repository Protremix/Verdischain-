import re

with open("/opt/verdis-chain/runtime/src/lib.rs", "r") as f:
    content = f.read()

# Fix 1: BuildStorage import - remove from the sp_runtime import line
content = content.replace(
    "ApplyExtrinsicResult, BuildStorage, ExtrinsicInclusionMode, MultiSignature, Perbill,",
    "ApplyExtrinsicResult, ExtrinsicInclusionMode, MultiSignature, Perbill,"
)

# Add BuildStorage import with cfg after NativeVersion
content = content.replace(
    '#[cfg(feature = "std")]\nuse sp_version::NativeVersion;',
    '#[cfg(feature = "std")]\nuse sp_version::NativeVersion;\n#[cfg(any(feature = "std", test))]\npub use sp_runtime::BuildStorage;'
)

# Fix 2: Add Executive type alias before construct_runtime
exec_alias = "/// Executive: handles dispatch to the various modules.\ntype Executive = frame_executive::Executive<Runtime, Block, frame_system::ChainContext, Runtime, AllPalletsWithSystem>;"
content = content.replace(
    "// === Construct Runtime ===",
    exec_alias + "\n\n// === Construct Runtime ==="
)

# Fix 3: impl_opaque_keys - use Babe and Grandpa instance names instead of crate names
content = content.replace(
    "pub babe: pallet_babe,",
    "pub babe: Babe,"
)
content = content.replace(
    "pub grandpa: pallet_grandpa,",
    "pub grandpa: Grandpa,"
)

# Fix 4: construct_runtime - the old construct_runtime! macro generates AllPalletsWithSystem
# but we need to make sure it's available. The construct_runtime! macro should handle this.

# Fix 5: pallet_babe and pallet_grandpa used in Config impls - need to use crate names for those
# The Config impls use pallet_babe::Config which is correct (crate::module)
# Only impl_opaque_keys needs the instance names

with open("/opt/verdis-chain/runtime/src/lib.rs", "w") as f:
    f.write(content)
print("Fixed runtime lib.rs")
