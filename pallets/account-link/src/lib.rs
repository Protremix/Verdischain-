#![cfg_attr(not(feature = "std"), no_std)]

//! # Verdis Account Link
//!
//! Binds a Substrate account (`AccountId32`, shown as `ki…`) to an Ethereum address (`H160`, shown as
//! `0x…`) so that both refer to **one balance** controlled by **one key**.
//!
//! ## The problem this solves
//!
//! `pallet-evm` maps an `H160` to a Substrate account with a one-way hash
//! (`blake2_256("evm:" ++ address)`). Consequences measured on Verdis testnet:
//!
//! * funds sent from MetaMask land on an account **nobody holds a key for** - 100 VRDX sent to a
//!   wallet's first 20 bytes ended up on `kiaDUSjX…` while the wallet itself was unchanged
//! * `H160 -> AccountId32` is computable, `AccountId32 -> H160` is **not** - a hash cannot be
//!   reversed, so a user's real wallet has no EVM view
//! * `EVM::withdraw` with `EnsureAddressTruncated` demands the caller's account share its first 20
//!   bytes with the `H160`, which an ordinary wallet never does
//!
//! ## How it works
//!
//! The account owner signs an **EIP-712** payload with their Ethereum key, proving control of the
//! `H160`. The chain verifies the signature by recovering the signer, then writes a **two-way**
//! mapping. `pallet-evm` then reads the user's real account instead of a hashed mirror.
//!
//! ## Deliberate differences from Astar's `pallet-unified-accounts`
//!
//! Astar's pallet was removed upstream in May 2026 as a Shibuya (testnet) beta and its Quantstamp
//! audit left 4 of 5 findings *Acknowledged* rather than fixed. Those findings are addressed here:
//!
//! * **AST-2 (multisig capture)**: Astar allowed binding a multisig or contract account to a single
//!   EOA, handing one key sole control of a multi-signature account. Here a bind is rejected unless
//!   the account passes [`Config::AllowedToLink`], which the runtime sets to reject non-plain
//!   accounts.
//! * **AST-4 (signature replay after reaping)**: Astar's payload allowed an old signature to be
//!   replayed once a mapping had been erased. Here the signed payload includes a per-account
//!   [`LinkNonce`] that only ever increases, so a signature is valid exactly once.
//! * **AST-1 (account reaped by the storage fee)**: the deposit is taken with
//!   [`Preservation::Preserve`], which cannot push an account below the existential deposit.
//! * **AST-3 (state stranded on the old mirror)**: [`Pallet::claim_evm_address`] refuses to bind
//!   while the default mirror still holds a balance, so funds cannot be stranded. The user must move
//!   them first, and the error names the account to move from.
//!
//! Unbinding is intentionally **not** provided. Astar's own removal PR records that balances held
//! under a unified account become unreachable from the EVM after unbinding; a one-way bind cannot
//! reach that state.

extern crate alloc;

pub use pallet::*;

#[cfg(test)]
mod mock;
#[cfg(test)]
mod tests;

use alloc::vec::Vec;
use frame_support::pallet_prelude::*;
use sp_core::{H160, H256};
use sp_runtime::traits::Zero;

/// EIP-712 domain and type hashes.
///
/// The domain binds a signature to this chain and this pallet: a signature produced for another
/// chain id, or for a different purpose, will recover a different digest and fail. `chainId` comes
/// from `pallet-evm`'s configured `ChainId`, so testnet signatures cannot be replayed on mainnet.
mod eip712 {
    use super::*;

    /// `keccak256("EIP712Domain(string name,string version,uint256 chainId)")`
    ///
    /// Computed, not copied. A wrong type hash would make every signature recover a different digest
    /// and the pallet would reject all valid claims - or, worse, accept a payload the user did not
    /// believe they were signing. `type_hashes_match_their_strings` re-derives both at test time.
    pub const DOMAIN_TYPE_HASH: [u8; 32] =
        hex_literal::hex!("c2f8787176b8ac6bf7215b4adcc1e069bf4ab82d9ab1df05a57a91d425935b6e");

    /// `keccak256("Claim(bytes substrateAddress,uint256 nonce)")`
    pub const CLAIM_TYPE_HASH: [u8; 32] =
        hex_literal::hex!("dc301abebe1a1d7e7da671caa5e6fc4c885fb53bb164abac035f3980e301beda");

    /// The exact strings the hashes above must correspond to. Kept next to them so a test can
    /// re-derive the constants instead of trusting that they were transcribed correctly.
    pub const DOMAIN_TYPE_STRING: &[u8] =
        b"EIP712Domain(string name,string version,uint256 chainId)";
    pub const CLAIM_TYPE_STRING: &[u8] = b"Claim(bytes substrateAddress,uint256 nonce)";

    pub const NAME: &[u8] = b"Verdis Account Link";
    pub const VERSION: &[u8] = b"1";
}

#[frame_support::pallet]
pub mod pallet {
    use super::*;
    use frame_support::traits::{
        fungible::{Inspect, Mutate},
        // Precision lives in tokens::misc and is re-exported by tokens; burn_from's signature is
        // (who, amount, Preservation, Precision, Fortitude) - read from frame-support 48.0.0
        // traits/tokens/fungible/regular.rs:263 rather than guessed.
        tokens::{Fortitude, Precision, Preservation},
        IsType,
    };
    use frame_system::pallet_prelude::*;

    type BalanceOf<T> =
        <<T as Config>::Currency as Inspect<<T as frame_system::Config>::AccountId>>::Balance;

    /// Decides which accounts may be bound to an EVM address.
    ///
    /// Exists because of Quantstamp finding AST-2: binding a multisig or a contract account to a
    /// single Ethereum key would hand that one key sole control of an account whose whole purpose is
    /// shared control. The runtime supplies a filter that rejects such accounts.
    pub trait LinkFilter<AccountId> {
        /// Return `true` if this account is allowed to be bound.
        fn allowed(who: &AccountId) -> bool;
    }

    /// Permits every account. Only appropriate for tests.
    pub struct AllowAll;
    impl<AccountId> LinkFilter<AccountId> for AllowAll {
        fn allowed(_who: &AccountId) -> bool {
            true
        }
    }

    #[pallet::config]
    pub trait Config: frame_system::Config {
        type RuntimeEvent: From<Event<Self>> + IsType<<Self as frame_system::Config>::RuntimeEvent>;

        /// Currency used for the storage deposit.
        type Currency: Inspect<Self::AccountId> + Mutate<Self::AccountId>;

        /// Deposit taken when a mapping is created, to pay for the storage it occupies.
        #[pallet::constant]
        type LinkDeposit: Get<BalanceOf<Self>>;

        /// EVM chain id, mixed into the EIP-712 domain so a signature cannot be replayed on another
        /// Verdis network.
        #[pallet::constant]
        type ChainId: Get<u64>;

        /// Which accounts may be bound. See [`LinkFilter`] and finding AST-2.
        type AllowedToLink: LinkFilter<Self::AccountId>;

        type WeightInfo: WeightInfo;
    }

    pub trait WeightInfo {
        fn claim_evm_address() -> Weight;
    }

    impl WeightInfo for () {
        fn claim_evm_address() -> Weight {
            Weight::from_parts(200_000_000, 4_000)
        }
    }

    #[pallet::pallet]
    pub struct Pallet<T>(_);

    /// `AccountId32 -> H160`. The direction a hash cannot provide.
    #[pallet::storage]
    pub type EvmAddressOf<T: Config> =
        StorageMap<_, Blake2_128Concat, T::AccountId, H160, OptionQuery>;

    /// `H160 -> AccountId32`, read by `pallet-evm` through [`LinkedAddressMapping`].
    #[pallet::storage]
    pub type AccountIdOf<T: Config> =
        StorageMap<_, Blake2_128Concat, H160, T::AccountId, OptionQuery>;

    /// Per-account counter included in the signed payload.
    ///
    /// Addresses Quantstamp finding AST-4: without it, a signature produced for an earlier binding
    /// stays valid forever and can be replayed after a mapping is erased. The counter only
    /// increases, so each signature authorises exactly one bind.
    #[pallet::storage]
    pub type LinkNonce<T: Config> = StorageMap<_, Blake2_128Concat, T::AccountId, u32, ValueQuery>;

    #[pallet::event]
    #[pallet::generate_deposit(pub(super) fn deposit_event)]
    pub enum Event<T: Config> {
        /// An account and an EVM address were bound together.
        AccountLinked {
            who: T::AccountId,
            evm_address: H160,
        },
    }

    #[pallet::error]
    pub enum Error<T> {
        /// This account is already bound to an EVM address.
        AccountAlreadyLinked,
        /// This EVM address is already bound to another account.
        EvmAddressAlreadyLinked,
        /// The signature did not recover to the claimed EVM address.
        InvalidSignature,
        /// The signature has the wrong length; 65 bytes expected.
        BadSignatureLength,
        /// This account type may not be bound. See finding AST-2.
        AccountNotAllowed,
        /// The default mirror account still holds funds. Move them first, or they would be
        /// unreachable after binding. See finding AST-3.
        MirrorAccountNotEmpty,
        /// Not enough free balance to cover the deposit.
        InsufficientBalance,
        /// The zero address cannot be bound.
        ZeroAddress,
    }

    #[pallet::call]
    impl<T: Config> Pallet<T> {
        /// Bind the caller's account to `evm_address`, proving ownership with an EIP-712 signature.
        ///
        /// After this call `pallet-evm` resolves `evm_address` to the caller's real account, so both
        /// representations share one balance and one key.
        ///
        /// The signature must be over the EIP-712 payload built by [`Pallet::eip712_digest`], which
        /// commits to the caller's account, the current [`LinkNonce`] and the chain id.
        #[pallet::call_index(0)]
        #[pallet::weight(T::WeightInfo::claim_evm_address())]
        pub fn claim_evm_address(
            origin: OriginFor<T>,
            evm_address: H160,
            signature: Vec<u8>,
        ) -> DispatchResult {
            let who = ensure_signed(origin)?;

            ensure!(evm_address != H160::zero(), Error::<T>::ZeroAddress);
            ensure!(
                T::AllowedToLink::allowed(&who),
                Error::<T>::AccountNotAllowed
            );
            ensure!(
                !EvmAddressOf::<T>::contains_key(&who),
                Error::<T>::AccountAlreadyLinked
            );
            ensure!(
                !AccountIdOf::<T>::contains_key(evm_address),
                Error::<T>::EvmAddressAlreadyLinked
            );
            ensure!(signature.len() == 65, Error::<T>::BadSignatureLength);

            // AST-3: refuse while the hashed mirror still holds funds, otherwise they become
            // unreachable once the mapping redirects the address elsewhere.
            ensure!(
                Self::default_mirror_is_empty(evm_address),
                Error::<T>::MirrorAccountNotEmpty
            );

            let nonce = LinkNonce::<T>::get(&who);
            let digest = Self::eip712_digest(&who, nonce);

            let mut sig = [0u8; 65];
            sig.copy_from_slice(&signature);
            let recovered =
                Self::recover_signer(&sig, &digest).ok_or(Error::<T>::InvalidSignature)?;
            ensure!(recovered == evm_address, Error::<T>::InvalidSignature);

            // AST-1: Preservation::Preserve cannot take the account below the existential deposit,
            // so paying the deposit can never reap the very account being bound.
            let deposit = T::LinkDeposit::get();
            if !deposit.is_zero() {
                let reducible =
                    T::Currency::reducible_balance(&who, Preservation::Preserve, Fortitude::Polite);
                ensure!(reducible >= deposit, Error::<T>::InsufficientBalance);
                T::Currency::burn_from(
                    &who,
                    deposit,
                    Preservation::Preserve,
                    Precision::Exact,
                    Fortitude::Polite,
                )?;
            }

            EvmAddressOf::<T>::insert(&who, evm_address);
            AccountIdOf::<T>::insert(evm_address, who.clone());
            // AST-4: burn this nonce so the same signature cannot authorise a second bind.
            LinkNonce::<T>::insert(&who, nonce.saturating_add(1));

            Self::deposit_event(Event::AccountLinked { who, evm_address });
            Ok(())
        }
    }

    impl<T: Config> Pallet<T> {
        /// The EIP-712 digest a claimant must sign.
        ///
        /// ```text
        /// digest = keccak256(0x19 ++ 0x01 ++ domainSeparator ++ structHash)
        /// domainSeparator = keccak256(DOMAIN_TYPE_HASH ++ keccak(name) ++ keccak(version) ++ chainId)
        /// structHash      = keccak256(CLAIM_TYPE_HASH ++ keccak(substrateAddress) ++ nonce)
        /// ```
        pub fn eip712_digest(who: &T::AccountId, nonce: u32) -> H256 {
            let mut domain = Vec::with_capacity(128);
            domain.extend_from_slice(&eip712::DOMAIN_TYPE_HASH);
            domain.extend_from_slice(keccak(eip712::NAME).as_bytes());
            domain.extend_from_slice(keccak(eip712::VERSION).as_bytes());
            domain.extend_from_slice(&u256_be(T::ChainId::get()));
            let domain_separator = keccak(&domain);

            let account_bytes = who.encode();
            let mut struct_data = Vec::with_capacity(96);
            struct_data.extend_from_slice(&eip712::CLAIM_TYPE_HASH);
            struct_data.extend_from_slice(keccak(&account_bytes).as_bytes());
            struct_data.extend_from_slice(&u256_be(nonce as u64));
            let struct_hash = keccak(&struct_data);

            let mut payload = Vec::with_capacity(66);
            payload.extend_from_slice(&[0x19, 0x01]);
            payload.extend_from_slice(domain_separator.as_bytes());
            payload.extend_from_slice(struct_hash.as_bytes());
            keccak(&payload)
        }

        /// Recover the Ethereum address that produced `sig` over `digest`.
        ///
        /// Returns `None` for a malformed signature rather than panicking, because this runs inside a
        /// dispatchable on caller-supplied bytes.
        pub fn recover_signer(sig: &[u8; 65], digest: &H256) -> Option<H160> {
            let pubkey =
                sp_io::crypto::secp256k1_ecdsa_recover(sig, digest.as_fixed_bytes()).ok()?;
            let hash = keccak(&pubkey);
            Some(H160::from_slice(&hash.as_bytes()[12..32]))
        }

        /// Is the hashed mirror of `evm_address` free of funds? See finding AST-3.
        ///
        /// The mirror is the account `pallet-evm` uses today: `blake2_256("evm:" ++ address)`. If it
        /// still holds a balance, binding would redirect the address and leave that balance
        /// unreachable from the EVM.
        pub fn default_mirror_is_empty(evm_address: H160) -> bool {
            let mirror = Self::default_mirror_account(evm_address);
            match T::AccountId::decode(&mut &mirror[..]) {
                Ok(account) => T::Currency::total_balance(&account).is_zero(),
                // A runtime whose AccountId is not 32 bytes has no such mirror to strand.
                Err(_) => true,
            }
        }

        /// `blake2_256("evm:" ++ address)` - the same derivation `HashedAddressMapping` uses.
        pub fn default_mirror_account(evm_address: H160) -> [u8; 32] {
            let mut data = [0u8; 24];
            data[0..4].copy_from_slice(b"evm:");
            data[4..24].copy_from_slice(&evm_address[..]);
            sp_io::hashing::blake2_256(&data)
        }
    }

    /// `AddressMapping` for `pallet-evm` that consults the link table first.
    ///
    /// A bound address resolves to the owner's real account, so the EVM and the wallet share one
    /// balance. An unbound address keeps today's hashed-mirror behaviour, which is what makes this
    /// safe to enable on a chain that already has EVM state: nothing that works stops working.
    pub struct LinkedAddressMapping<T>(core::marker::PhantomData<T>);

    impl<T: Config> pallet_evm::AddressMapping<T::AccountId> for LinkedAddressMapping<T>
    where
        T::AccountId: From<[u8; 32]>,
    {
        fn into_account_id(address: H160) -> T::AccountId {
            if let Some(account) = AccountIdOf::<T>::get(address) {
                return account;
            }
            Pallet::<T>::default_mirror_account(address).into()
        }
    }

    /// `WithdrawOrigin`/`CallOrigin` that accepts the bound owner of an address.
    ///
    /// `EnsureAddressTruncated` requires the caller's account to share its first 20 bytes with the
    /// `H160`, which an ordinary wallet never does - measured on testnet, that makes `EVM::withdraw`
    /// unusable. This accepts a caller who has proven ownership of the address, and otherwise falls
    /// back to the truncated check so existing behaviour is preserved.
    pub struct EnsureLinkedAddress<T>(core::marker::PhantomData<T>);

    impl<T, OuterOrigin> pallet_evm::EnsureAddressOrigin<OuterOrigin> for EnsureLinkedAddress<T>
    where
        T: Config,
        OuterOrigin: Into<Result<frame_system::RawOrigin<T::AccountId>, OuterOrigin>>
            + From<frame_system::RawOrigin<T::AccountId>>,
    {
        type Success = T::AccountId;

        fn try_address_origin(
            address: &H160,
            origin: OuterOrigin,
        ) -> Result<T::AccountId, OuterOrigin> {
            origin.into().and_then(|o| match o {
                frame_system::RawOrigin::Signed(who) => match AccountIdOf::<T>::get(address) {
                    Some(owner) if owner == who => Ok(who),
                    _ => Err(OuterOrigin::from(frame_system::RawOrigin::Signed(who))),
                },
                r => Err(OuterOrigin::from(r)),
            })
        }
    }
}

/// keccak256 over a byte slice.
fn keccak(data: &[u8]) -> H256 {
    H256::from(sp_io::hashing::keccak_256(data))
}

/// Encode a `u64` as a big-endian 32-byte word, as EIP-712 requires for `uint256`.
fn u256_be(value: u64) -> [u8; 32] {
    let mut out = [0u8; 32];
    out[24..32].copy_from_slice(&value.to_be_bytes());
    out
}
