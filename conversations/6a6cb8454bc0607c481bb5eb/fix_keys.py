import re, sys

with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "r") as f:
    content = f.read()

pattern = r'/// Build a session-keys vector.*?fn build_session_keys\(uris: &\[&str\]\) -> Vec<\(AccountId, AccountId, SessionKeys\)> \{.*?\n\}'
match = re.search(pattern, content, re.DOTALL)
if not match:
    print("FAIL - could not find function")
    sys.exit(1)

old_fn = match.group()

new_fn = '''/// Build a session-keys vector for the given list of URIs.
fn build_session_keys(uris: &[&str]) -> Vec<(AccountId, AccountId, SessionKeys)> {
    uris.iter()
        .enumerate()
        .map(|(i, uri)| {
            match i {
                0 => {
                    let controller = Sr25519Keyring::Alice.to_account_id();
                    (controller.clone(), controller, SessionKeys {
                        babe: Sr25519Keyring::Alice.public().into(),
                        grandpa: Ed25519Keyring::Alice.public().into(),
                    })
                }
                1 => {
                    let controller = Sr25519Keyring::Bob.to_account_id();
                    (controller.clone(), controller, SessionKeys {
                        babe: Sr25519Keyring::Bob.public().into(),
                        grandpa: Ed25519Keyring::Bob.public().into(),
                    })
                }
                2 => {
                    let controller = Sr25519Keyring::Charlie.to_account_id();
                    (controller.clone(), controller, SessionKeys {
                        babe: Sr25519Keyring::Charlie.public().into(),
                        grandpa: Ed25519Keyring::Charlie.public().into(),
                    })
                }
                3 => {
                    let controller = Sr25519Keyring::Dave.to_account_id();
                    (controller.clone(), controller, SessionKeys {
                        babe: Sr25519Keyring::Dave.public().into(),
                        grandpa: Ed25519Keyring::Dave.public().into(),
                    })
                }
                4 => {
                    let controller = Sr25519Keyring::Eve.to_account_id();
                    (controller.clone(), controller, SessionKeys {
                        babe: Sr25519Keyring::Eve.public().into(),
                        grandpa: Ed25519Keyring::Eve.public().into(),
                    })
                }
                5 => {
                    let controller = Sr25519Keyring::Ferdie.to_account_id();
                    (controller.clone(), controller, SessionKeys {
                        babe: Sr25519Keyring::Ferdie.public().into(),
                        grandpa: Ed25519Keyring::Ferdie.public().into(),
                    })
                }
                _ => {
                    let pair = sr_from(&format!("//{}", uri));
                    let controller: AccountId = pair.public().into();
                    (controller.clone(), controller, SessionKeys {
                        babe: pair.public().into(),
                        grandpa: ed_from(&format!("//{}", uri)).public().into(),
                    })
                }
            }
        })
        .collect()
}'''

content = content.replace(old_fn, new_fn)
with open("/opt/verdis-chain-rust/node/src/chain_spec.rs", "w") as f:
    f.write(content)
print("OK - function rewritten")
