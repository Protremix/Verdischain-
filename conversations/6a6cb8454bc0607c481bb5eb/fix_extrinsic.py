import re

with open("/opt/verdis-chain/runtime/src/lib.rs", "r") as f:
    content = f.read()

# Update SignedExtra to TxExtension with frame v48 types
old_signed_extra = '''/// Signed extra data for transactions
pub type SignedExtra = (
    frame_system::CheckNonZeroSender<Runtime>,
    frame_system::CheckSpecVersion<Runtime>,
    frame_system::CheckTxVersion<Runtime>,
    frame_system::CheckGenesis<Runtime>,
    frame_system::CheckMortality<Runtime>,
    frame_system::CheckNonce<Runtime>,
    frame_system::CheckWeight<Runtime>,
    pallet_transaction_payment::ChargeTransactionPayment<Runtime>,
);'''

new_tx_extension = '''/// Transaction extension data for transactions (frame v48)
pub type SignedExtra = (
    frame_system::CheckNonZeroSender<Runtime>,
    frame_system::CheckSpecVersion<Runtime>,
    frame_system::CheckTxVersion<Runtime>,
    frame_system::CheckGenesis<Runtime>,
    frame_system::CheckMortality<Runtime>,
    frame_system::CheckNonce<Runtime>,
    frame_system::CheckWeight<Runtime>,
    pallet_transaction_payment::ChargeTransactionPayment<Runtime>,
);

/// The UncheckedExtrinsic type with frame v48 extensions
pub type UncheckedExtrinsic = generic::UncheckedExtrinsic<
    Address,
    RuntimeCall,
    Signature,
    SignedExtra,
    sp_runtime::traits::InvalidVersion,
    MaxEncodedLen,
>;

/// Max encoded length constant
pub const MaxEncodedLen: u32 = 16777216; // 16 MiB'''

content = content.replace(old_signed_extra, new_tx_extension)

# Also need to remove the old UncheckedExtrinsic definition
old_unchecked = '''/// The UncheckedExtrinsic type
pub type UncheckedExtrinsic = generic::UncheckedExtrinsic<Address, RuntimeCall, Signature, SignedExtra>;'''

content = content.replace(old_unchecked, '''/// (Old UncheckedExtrinsic replaced above with frame v48 version)''')

with open("/opt/verdis-chain/runtime/src/lib.rs", "w") as f:
    f.write(content)
print("Updated UncheckedExtrinsic and SignedExtra for frame v48")
