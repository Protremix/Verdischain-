import sys

FILE_PATH = "/opt/verdis-chain-rust/pallets/tokenomics/src/lib.rs"

with open(FILE_PATH, "r") as f:
    content = f.read()

# Find the closing brace of the test module - it's the line before `#[cfg(test)]\nmod economic_invariants;`
marker = "\n}\n\n#[cfg(test)]\nmod economic_invariants;"
idx = content.find(marker)
if idx == -1:
    print("ERROR: Could not find test module closing brace marker")
    sys.exit(1)

NEW_TESTS = """
    #[test]
    fn test_give_consent_duplicate_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(alice.clone())));
            assert_noop!(
                Tokenomics::give_consent(RuntimeOrigin::signed(alice)),
                Error::<Test>::AlreadyConsented
            );
        });
    }

    #[test]
    fn test_purchase_without_consent_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Tokenomics::purchase(
                    RuntimeOrigin::signed(alice),
                    1_000_000
                ),
                Error::<Test>::ConsentRequired
            );
        });
    }

    #[test]
    fn test_purchase_zero_amount_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            Tokenomics::give_consent(RuntimeOrigin::signed(alice.clone())).unwrap();
            assert_noop!(
                Tokenomics::purchase(
                    RuntimeOrigin::signed(alice),
                    0
                ),
                Error::<Test>::ZeroAmount
            );
        });
    }

    #[test]
    fn test_set_inflation_rate_non_root_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Tokenomics::set_inflation_rate(
                    RuntimeOrigin::signed(alice),
                    500
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_set_inflation_rate_too_high_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Tokenomics::set_inflation_rate(
                    RuntimeOrigin::root(),
                    1001
                ),
                Error::<Test>::InflationRateTooHigh
            );
        });
    }

    #[test]
    fn test_set_inflation_rate_works() {
        new_test_ext().execute_with(|| {
            assert_ok!(Tokenomics::set_inflation_rate(RuntimeOrigin::root(), 500));
            assert_eq!(AnnualInflationRate::<Test>::get(), 500);
        });
    }

    #[test]
    fn test_release_distribution_non_root_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_noop!(
                Tokenomics::release_distribution(
                    RuntimeOrigin::signed(alice),
                    b"ecosystem".to_vec(),
                    1_000_000
                ),
                sp_runtime::DispatchError::BadOrigin
            );
        });
    }

    #[test]
    fn test_release_distribution_invalid_category_rejected() {
        new_test_ext().execute_with(|| {
            assert_noop!(
                Tokenomics::release_distribution(
                    RuntimeOrigin::root(),
                    b"nonexistent_category".to_vec(),
                    1_000_000
                ),
                Error::<Test>::InvalidCategory
            );
        });
    }

    #[test]
    fn test_give_consent_works_and_verified() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            assert_ok!(Tokenomics::give_consent(RuntimeOrigin::signed(alice.clone())));
            assert!(ConsentGiven::<Test>::get(&alice).unwrap_or(false));
        });
    }

    #[test]
    fn test_update_presale_price_works() {
        new_test_ext().execute_with(|| {
            assert_ok!(Tokenomics::update_presale_price(RuntimeOrigin::root(), 500));
            assert_eq!(PresalePrice::<Test>::get(), 500);
        });
    }

    #[test]
    fn test_purchase_exceeds_allocation_rejected() {
        new_test_ext().execute_with(|| {
            let alice = Sr25519Keyring::Alice.to_account_id();
            Tokenomics::give_consent(RuntimeOrigin::signed(alice.clone())).unwrap();
            // InvestorAllocation = 12B (12_000_000_000_000_000_000)
            // Try to purchase more than allocation
            assert_noop!(
                Tokenomics::purchase(
                    RuntimeOrigin::signed(alice),
                    13_000_000_000_000_000_000u128
                ),
                Error::<Test>::MaxInvestorAllocationReached
            );
        });
    }

    #[test]
    fn test_release_distribution_category_too_long_rejected() {
        new_test_ext().execute_with(|| {
            let long_cat = vec![b'X'; 40]; // Max category length is 32
            assert_noop!(
                Tokenomics::release_distribution(
                    RuntimeOrigin::root(),
                    long_cat,
                    1_000_000
                ),
                Error::<Test>::InvalidCategory
            );
        });
    }
"""

# Insert before the closing brace
new_content = content[:idx] + NEW_TESTS + content[idx:]

with open(FILE_PATH, "w") as f:
    f.write(new_content)

print(f"Inserted 12 tokenomics security tests")
