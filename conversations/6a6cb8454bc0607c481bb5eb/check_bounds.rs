use super::*;

// Test each Checkable sub-bound individually to find which one fails
fn _assert_member<T: sp_runtime::traits::Member>(_t: T) {}
fn _assert_maybe_display<T: sp_runtime::traits::MaybeDisplay>(_t: T) {}
fn _assert_encode<T: codec::Encode>(_t: T) {}
fn _assert_verify<T: sp_runtime::traits::Verify>(_t: T) {}
fn _assert_identify_account<T: sp_runtime::traits::IdentifyAccount>(_t: T) {}
fn _assert_transaction_extension<E, C: sp_runtime::traits::Dispatchable>(_e: E) where E: sp_runtime::traits::TransactionExtension<C> {}
fn _assert_lookup<T: sp_runtime::traits::Lookup>(_t: T) {}

// The actual Checkable bound
fn _assert_checkable() where
    UncheckedExtrinsic: sp_runtime::traits::Checkable<frame_system::ChainContext<Runtime>>
{}

// Individual bounds
fn _assert_address_member() where Address: sp_runtime::traits::Member {}
fn _assert_address_maybe_display() where Address: sp_runtime::traits::MaybeDisplay {}
fn _assert_call_dispatchable() where RuntimeCall: sp_runtime::traits::Dispatchable {}
fn _assert_call_member() where RuntimeCall: sp_runtime::traits::Member {}
fn _assert_call_encode() where RuntimeCall: codec::Encode {}
fn _assert_signature_verify() where Signature: sp_runtime::traits::Verify {}
fn _assert_extra_encode() where SignedExtra: codec::Encode {}
fn _assert_extra_txext() where SignedExtra: sp_runtime::traits::TransactionExtension<RuntimeCall> {}
fn _assert_accountid_member() where AccountId: sp_runtime::traits::Member {}
fn _assert_accountid_maybe_display() where AccountId: sp_runtime::traits::MaybeDisplay {}
fn _assert_chaincontext_lookup() where frame_system::ChainContext<Runtime>: sp_runtime::traits::Lookup {}
