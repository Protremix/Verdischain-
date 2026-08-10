#!/usr/bin/env python3
"""Apply GulfStream and IBC security fixes to the Verdis Chain codebase."""
import subprocess
import sys

def run(cmd, timeout=60):
    """Run a command on the server."""
    result = subprocess.run(
        ["ssh", "root@91.98.160.145", cmd],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout + result.stderr

# Fix 1: GulfStream - Add ValidatorChecker trait to Config
print("=== Fix 1: GulfStream ensure_active_validator ===")
fix_gulf_config = r'''cd /opt/verdis-chain-rust && python3 -c "
import re
with open('pallets/gulf-stream/src/lib.rs', 'r') as f:
    content = f.read()

# Add ValidatorChecker trait to Config
old_config = '''    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxPendingForwards: Get<u32>;
        type MaxForwardedHistory: Get<u32>;
    }'''

new_config = '''    /// Trait for checking if an account is an active validator.
    /// Implemented by the runtime to connect to the DPoS pallet.
    pub trait ValidatorChecker {
        fn is_active_validator(who: &T::AccountId) -> bool;
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxPendingForwards: Get<u32>;
        type MaxForwardedHistory: Get<u32>;
        /// Validator checker — connects to DPoS active validator set.
        type ValidatorChecker: ValidatorChecker;
    }'''

# Note: the trait uses T::AccountId which needs to reference the Config's AccountId
# Fix: use a generic parameter or reference frame_system
new_config = '''    /// Trait for checking if an account is an active validator.
    /// Implemented by the runtime to connect to the DPoS pallet.
    pub trait ValidatorChecker<AccountId> {
        fn is_active_validator(who: &AccountId) -> bool;
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type MaxPendingForwards: Get<u32>;
        type MaxForwardedHistory: Get<u32>;
        /// Validator checker — connects to DPoS active validator set.
        type ValidatorChecker: ValidatorChecker<Self::AccountId>;
    }'''

content = content.replace(old_config, new_config)

# Fix ensure_active_validator to use the trait
old_fn = '''        /// Check if the caller is an active validator
        fn ensure_active_validator(_who: &T::AccountId) -> Result<(), Error<T>> {
            // In production, this would check the DPoS validator set
            // For now, accept any signed caller as relayer/validator
            Ok(())
        }'''

new_fn = '''        /// Check if the caller is an active validator
        fn ensure_active_validator(who: &T::AccountId) -> Result<(), Error<T>> {
            ensure!(
                T::ValidatorChecker::is_active_validator(who),
                Error::<T>::NotActiveValidator
            );
            Ok(())
        }'''

content = content.replace(old_fn, new_fn)

# Add NotActiveValidator error if not present
if 'NotActiveValidator' not in content:
    old_errors = '''    #[pallet::error]
    pub enum Error<T> {'''
    new_errors = '''    #[pallet::error]
    pub enum Error<T> {
        /// Caller is not an active validator
        NotActiveValidator,'''
    content = content.replace(old_errors, new_errors)

with open('pallets/gulf-stream/src/lib.rs', 'w') as f:
    f.write(content)
print('GulfStream pallet fixed')
"'''

result = run(fix_gulf_config, timeout=30)
print(result)

# Fix 2: IBC - Add channel state check in timeout_packet
print("\n=== Fix 2: IBC timeout_packet channel state check ===")
fix_ibc = r'''cd /opt/verdis-chain-rust && python3 -c "
with open('pallets/ibc/src/lib.rs', 'r') as f:
    content = f.read()

# Fix timeout_packet: add channel state check and fix error message
old_code = '''        pub fn timeout_packet(
            origin: OriginFor<T>,
            channel_id: u32,
            sequence: u64,
        ) -> DispatchResult {
            // SECURITY: Any signed relayer can call timeout, but packet must not be acknowledged
            let _relayer = ensure_signed(origin)?;

            let packet =
                IbcPackets::<T>::get((channel_id, sequence)).ok_or(Error::<T>::ChannelNotFound)?;

            // SECURITY: Verify the packet has actually timed out
            let current_height: u64 = frame_system::Pallet::<T>::block_number()
                .try_into()
                .unwrap_or(0);
            ensure!(
                current_height >= packet.timeout_height,
                Error::<T>::PacketTimeout
            );'''

new_code = '''        pub fn timeout_packet(
            origin: OriginFor<T>,
            channel_id: u32,
            sequence: u64,
        ) -> DispatchResult {
            // SECURITY: Any signed relayer can call timeout, but packet must not be acknowledged
            let _relayer = ensure_signed(origin)?;

            // SECURITY: Verify channel exists and is not closed
            let channel =
                IbcChannels::<T>::get(channel_id).ok_or(Error::<T>::ChannelNotFound)?;
            ensure!(
                channel.state != 4, // 4 = Closed
                Error::<T>::ChannelNotOpen
            );

            let packet =
                IbcPackets::<T>::get((channel_id, sequence)).ok_or(Error::<T>::PacketNotFound)?;

            // SECURITY: Verify the packet has actually timed out
            let current_height: u64 = frame_system::Pallet::<T>::block_number()
                .try_into()
                .unwrap_or(0);
            ensure!(
                current_height >= packet.timeout_height,
                Error::<T>::PacketTimeout
            );'''

content = content.replace(old_code, new_code)

# Add PacketNotFound error if not present
if 'PacketNotFound' not in content:
    old_errors = '''    #[pallet::error]
    pub enum Error<T> {'''
    new_errors = '''    #[pallet::error]
    pub enum Error<T> {
        /// Packet not found in storage
        PacketNotFound,'''
    content = content.replace(old_errors, new_errors)

with open('pallets/ibc/src/lib.rs', 'w') as f:
    f.write(content)
print('IBC pallet fixed')
"'''

result = run(fix_ibc, timeout=30)
print(result)
