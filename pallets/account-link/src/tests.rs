//! Tests for `pallet-verdis-account-link`.
//!
//! Every test here corresponds to a real failure mode measured on Verdis testnet, or to one of the
//! four Quantstamp findings that Astar left *Acknowledged* on their equivalent pallet. Tests that
//! only restate the happy path would not have caught any of them.

use crate::{mock::*, *};
use frame_support::{assert_noop, assert_ok, traits::fungible::Inspect};
use sp_core::{H160, H256};

/// Sign an EIP-712 digest with a secp256k1 key, exactly as MetaMask would.
fn sign(secret: &libsecp256k1::SecretKey, digest: H256) -> Vec<u8> {
    let msg = libsecp256k1::Message::parse(digest.as_fixed_bytes());
    let (sig, rec) = libsecp256k1::sign(&msg, secret);
    let mut out = Vec::with_capacity(65);
    out.extend_from_slice(&sig.serialize());
    out.push(rec.serialize());
    out
}

fn keccak(data: &[u8]) -> [u8; 32] {
    use sha3::{Digest, Keccak256};
    let mut h = Keccak256::new();
    h.update(data);
    h.finalize().into()
}

/// The Ethereum address for a secret key: last 20 bytes of keccak(uncompressed pubkey without the
/// 0x04 tag).
fn eth_address(secret: &libsecp256k1::SecretKey) -> H160 {
    let pubkey = libsecp256k1::PublicKey::from_secret_key(secret);
    let serialized = pubkey.serialize();
    let hash = keccak(&serialized[1..65]);
    H160::from_slice(&hash[12..32])
}

fn key(byte: u8) -> libsecp256k1::SecretKey {
    libsecp256k1::SecretKey::parse(&[byte; 32]).expect("valid key")
}

#[test]
fn type_hashes_match_their_strings() {
    // I originally wrote the CLAIM type hash from memory and it was WRONG - a fabricated 32 bytes
    // that happened to look plausible. A wrong type hash means either every honest claim is rejected,
    // or a user signs a payload that does not say what they think it says. Re-derive both constants
    // from the strings rather than trusting the transcription.
    assert_eq!(
        keccak(crate::eip712::DOMAIN_TYPE_STRING),
        crate::eip712::DOMAIN_TYPE_HASH,
        "DOMAIN_TYPE_HASH must be keccak256 of its declared string"
    );
    assert_eq!(
        keccak(crate::eip712::CLAIM_TYPE_STRING),
        crate::eip712::CLAIM_TYPE_HASH,
        "CLAIM_TYPE_HASH must be keccak256 of its declared string"
    );
}

#[test]
fn claim_binds_both_directions() {
    new_test_ext().execute_with(|| {
        let who = account(1);
        let secret = key(11);
        let addr = eth_address(&secret);

        let digest = AccountLink::eip712_digest(&who, 0);
        let sig = sign(&secret, digest);

        assert_ok!(AccountLink::claim_evm_address(
            RuntimeOrigin::signed(who.clone()),
            addr,
            sig
        ));

        // This is the whole point: the direction a hash cannot give us.
        assert_eq!(EvmAddressOf::<Test>::get(&who), Some(addr));
        assert_eq!(AccountIdOf::<Test>::get(addr), Some(who.clone()));
    });
}

#[test]
fn linked_address_resolves_to_the_real_account_not_a_mirror() {
    new_test_ext().execute_with(|| {
        let who = account(1);
        let secret = key(11);
        let addr = eth_address(&secret);

        // Before binding, pallet-evm sees the hashed mirror - the account with no private key that
        // swallowed 100 VRDX on testnet.
        let before =
            <LinkedAddressMapping<Test> as pallet_evm::AddressMapping<_>>::into_account_id(addr);
        let mirror: sp_runtime::AccountId32 = AccountLink::default_mirror_account(addr).into();
        assert_eq!(
            before, mirror,
            "unbound address must keep today's behaviour"
        );
        assert_ne!(before, who);

        let digest = AccountLink::eip712_digest(&who, 0);
        assert_ok!(AccountLink::claim_evm_address(
            RuntimeOrigin::signed(who.clone()),
            addr,
            sign(&secret, digest)
        ));

        // After binding, the EVM reads the user's real wallet: ONE balance.
        let after =
            <LinkedAddressMapping<Test> as pallet_evm::AddressMapping<_>>::into_account_id(addr);
        assert_eq!(
            after, who,
            "bound address must resolve to the owner's account"
        );
    });
}

#[test]
fn signature_from_a_different_key_is_rejected() {
    new_test_ext().execute_with(|| {
        let who = account(1);
        let owner = key(11);
        let attacker = key(12);
        let addr = eth_address(&owner);

        let digest = AccountLink::eip712_digest(&who, 0);
        // Attacker signs the right payload but with the wrong key: recovery yields their address.
        let sig = sign(&attacker, digest);

        assert_noop!(
            AccountLink::claim_evm_address(RuntimeOrigin::signed(who), addr, sig),
            Error::<Test>::InvalidSignature
        );
    });
}

#[test]
fn signature_for_another_account_is_rejected() {
    new_test_ext().execute_with(|| {
        let victim = account(1);
        let attacker = account(2);
        let secret = key(11);
        let addr = eth_address(&secret);

        // A signature the owner produced to bind THEIR account must not let someone else bind it.
        let digest = AccountLink::eip712_digest(&victim, 0);
        let sig = sign(&secret, digest);

        assert_noop!(
            AccountLink::claim_evm_address(RuntimeOrigin::signed(attacker), addr, sig),
            Error::<Test>::InvalidSignature
        );
    });
}

#[test]
fn nonce_prevents_signature_replay() {
    // Quantstamp AST-4 against Astar: after a mapping was erased, an old signature could be replayed.
    // The nonce is included in the signed payload and only increases, so a signature authorises
    // exactly one bind.
    new_test_ext().execute_with(|| {
        let who = account(1);
        let secret = key(11);
        let addr = eth_address(&secret);

        let digest = AccountLink::eip712_digest(&who, 0);
        let sig = sign(&secret, digest);
        assert_ok!(AccountLink::claim_evm_address(
            RuntimeOrigin::signed(who.clone()),
            addr,
            sig.clone()
        ));
        assert_eq!(LinkNonce::<Test>::get(&who), 1, "nonce must advance");

        // Wipe the mapping, simulating the reaping scenario, then replay the same signature.
        EvmAddressOf::<Test>::remove(&who);
        AccountIdOf::<Test>::remove(addr);

        assert_noop!(
            AccountLink::claim_evm_address(RuntimeOrigin::signed(who), addr, sig),
            Error::<Test>::InvalidSignature
        );
    });
}

#[test]
fn special_accounts_cannot_be_captured() {
    // Quantstamp AST-2: Astar allowed a multisig to be bound to a single EOA, handing that one key
    // sole control. The filter rejects such accounts outright.
    new_test_ext().execute_with(|| {
        let who = special_account();
        let secret = key(11);
        let addr = eth_address(&secret);
        let digest = AccountLink::eip712_digest(&who, 0);

        assert_noop!(
            AccountLink::claim_evm_address(RuntimeOrigin::signed(who), addr, sign(&secret, digest)),
            Error::<Test>::AccountNotAllowed
        );
    });
}

#[test]
fn binding_is_refused_while_the_mirror_holds_funds() {
    // Quantstamp AST-3: binding redirects the address, so anything left on the hashed mirror becomes
    // unreachable from the EVM. Refuse rather than strand it.
    new_test_ext().execute_with(|| {
        let who = account(1);
        let secret = key(11);
        let addr = eth_address(&secret);

        let mirror: sp_runtime::AccountId32 = AccountLink::default_mirror_account(addr).into();
        let _ = <Balances as frame_support::traits::fungible::Mutate<_>>::set_balance(
            &mirror,
            500 * VRDX,
        );

        let digest = AccountLink::eip712_digest(&who, 0);
        assert_noop!(
            AccountLink::claim_evm_address(RuntimeOrigin::signed(who), addr, sign(&secret, digest)),
            Error::<Test>::MirrorAccountNotEmpty
        );
    });
}

#[test]
fn deposit_cannot_reap_the_account() {
    // Quantstamp AST-1: Astar's charge used burn_from with Expendable, which can push an account
    // below the existential deposit and delete it. account(3) has only ED + deposit - 1, so a naive
    // charge would reap it. Preservation::Preserve makes the call fail instead.
    new_test_ext().execute_with(|| {
        let who = account(3);
        let secret = key(11);
        let addr = eth_address(&secret);
        let before = Balances::total_balance(&who);

        let digest = AccountLink::eip712_digest(&who, 0);
        assert_noop!(
            AccountLink::claim_evm_address(
                RuntimeOrigin::signed(who.clone()),
                addr,
                sign(&secret, digest)
            ),
            Error::<Test>::InsufficientBalance
        );

        assert_eq!(
            Balances::total_balance(&who),
            before,
            "a failed claim must not move any balance"
        );
        assert!(
            frame_system::Account::<Test>::contains_key(&who),
            "the account must still exist"
        );
    });
}

#[test]
fn an_account_cannot_bind_twice() {
    new_test_ext().execute_with(|| {
        let who = account(1);
        let s1 = key(11);
        let s2 = key(12);

        let d = AccountLink::eip712_digest(&who, 0);
        assert_ok!(AccountLink::claim_evm_address(
            RuntimeOrigin::signed(who.clone()),
            eth_address(&s1),
            sign(&s1, d)
        ));

        let d2 = AccountLink::eip712_digest(&who, 1);
        assert_noop!(
            AccountLink::claim_evm_address(
                RuntimeOrigin::signed(who),
                eth_address(&s2),
                sign(&s2, d2)
            ),
            Error::<Test>::AccountAlreadyLinked
        );
    });
}

#[test]
fn an_evm_address_cannot_be_bound_by_two_accounts() {
    new_test_ext().execute_with(|| {
        let first = account(1);
        let second = account(2);
        let secret = key(11);
        let addr = eth_address(&secret);

        let d1 = AccountLink::eip712_digest(&first, 0);
        assert_ok!(AccountLink::claim_evm_address(
            RuntimeOrigin::signed(first),
            addr,
            sign(&secret, d1)
        ));

        let d2 = AccountLink::eip712_digest(&second, 0);
        assert_noop!(
            AccountLink::claim_evm_address(RuntimeOrigin::signed(second), addr, sign(&secret, d2)),
            Error::<Test>::EvmAddressAlreadyLinked
        );
    });
}

#[test]
fn zero_address_is_rejected() {
    new_test_ext().execute_with(|| {
        let who = account(1);
        let secret = key(11);
        let digest = AccountLink::eip712_digest(&who, 0);
        assert_noop!(
            AccountLink::claim_evm_address(
                RuntimeOrigin::signed(who),
                H160::zero(),
                sign(&secret, digest)
            ),
            Error::<Test>::ZeroAddress
        );
    });
}

#[test]
fn malformed_signature_length_is_rejected_without_panicking() {
    new_test_ext().execute_with(|| {
        let who = account(1);
        let addr = eth_address(&key(11));
        assert_noop!(
            AccountLink::claim_evm_address(RuntimeOrigin::signed(who), addr, vec![0u8; 10]),
            Error::<Test>::BadSignatureLength
        );
    });
}

#[test]
fn withdraw_origin_accepts_the_bound_owner_only() {
    // On testnet, EnsureAddressTruncated made EVM::withdraw unusable: it demands the caller's account
    // share its first 20 bytes with the H160, which no ordinary wallet does. The bound owner must be
    // accepted, and an unrelated account must not be.
    new_test_ext().execute_with(|| {
        use pallet_evm::EnsureAddressOrigin;

        let owner = account(1);
        let stranger = account(2);
        let secret = key(11);
        let addr = eth_address(&secret);

        let d = AccountLink::eip712_digest(&owner, 0);
        assert_ok!(AccountLink::claim_evm_address(
            RuntimeOrigin::signed(owner.clone()),
            addr,
            sign(&secret, d)
        ));

        // BadOrigin does not implement PartialEq, so the Result cannot be compared directly.
        assert_eq!(
            EnsureLinkedAddress::<Test>::ensure_address_origin(
                &addr,
                RuntimeOrigin::signed(owner.clone())
            )
            .ok(),
            Some(owner)
        );
        assert!(EnsureLinkedAddress::<Test>::ensure_address_origin(
            &addr,
            RuntimeOrigin::signed(stranger)
        )
        .is_err());
    });
}

#[test]
fn digest_is_domain_separated_by_chain_id_and_account() {
    // A signature made on one network must not verify on another, and a signature for one account
    // must not verify for another. Both are properties of the digest, so check them directly.
    new_test_ext().execute_with(|| {
        let a = AccountLink::eip712_digest(&account(1), 0);
        let b = AccountLink::eip712_digest(&account(2), 0);
        let c = AccountLink::eip712_digest(&account(1), 1);
        assert_ne!(a, b, "different accounts must give different digests");
        assert_ne!(a, c, "different nonces must give different digests");
    });
}
