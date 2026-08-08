#!/usr/bin/env python3
"""Fix chain_spec.rs to use URI-derived keypairs instead of non-existent keyring variants."""

with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "r") as f:
    content = f.read()

# Add helper functions after the use statement
old_use = "use sp_keyring::{Ed25519Keyring, Sr25519Keyring};"
new_use = '''use sp_keyring::{Ed25519Keyring, Sr25519Keyring};
use sp_core::sr25519::Pair as Sr25519Pair;
use sp_core::ed25519::Pair as Ed25519Pair;

fn sr_from(uri: &str) -> Sr25519Pair {
    Sr25519Pair::from_string(uri, None).expect("Invalid URI")
}
fn ed_from(uri: &str) -> Ed25519Pair {
    Ed25519Pair::from_string(uri, None).expect("Invalid URI")
}'''

content = content.replace(old_use, new_use)

# Replace all custom keyring references
# For Sr25519: to_account_id() -> public().into(), public().into() stays the same
# For Ed25519: public().into() stays the same
replacements = [
    ('Sr25519Keyring::George.to_account_id()', 'sr_from("//George").public().into()'),
    ('Sr25519Keyring::George.public().into()', 'sr_from("//George").public().into()'),
    ('Ed25519Keyring::George.public().into()', 'ed_from("//George").public().into()'),
    ('Sr25519Keyring::Hamilton.to_account_id()', 'sr_from("//Hamilton").public().into()'),
    ('Sr25519Keyring::Hamilton.public().into()', 'sr_from("//Hamilton").public().into()'),
    ('Ed25519Keyring::Hamilton.public().into()', 'ed_from("//Hamilton").public().into()'),
    ('Sr25519Keyring::Ian.to_account_id()', 'sr_from("//Ian").public().into()'),
    ('Sr25519Keyring::Ian.public().into()', 'sr_from("//Ian").public().into()'),
    ('Ed25519Keyring::Ian.public().into()', 'ed_from("//Ian").public().into()'),
    ('Sr25519Keyring::Kelly.to_account_id()', 'sr_from("//Kelly").public().into()'),
    ('Sr25519Keyring::Kelly.public().into()', 'sr_from("//Kelly").public().into()'),
    ('Ed25519Keyring::Kelly.public().into()', 'ed_from("//Kelly").public().into()'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "w") as f:
    f.write(content)

print("Fixed successfully!")
