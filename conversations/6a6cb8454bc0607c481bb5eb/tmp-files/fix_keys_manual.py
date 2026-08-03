import sys

with open("/dev/stdin", "r") as f:
    content = f.read()

# Add imports for manual key insertion
old_imports = "use sp_consensus_babe::BabeApi;\nuse sp_session;"
new_imports = """use sp_consensus_babe::BabeApi;
use sp_session;
use sp_keyring::Sr25519Keyring;
use sp_keystore::Keystore;
use sp_core::crypto::Pair;"""
content = content.replace(old_imports, new_imports)

# Replace the generate_initial_session_keys block with manual key insertion
old_block = """    // Generate initial session keys from dev key seed
    if let Some(ref seed) = config.dev_key_seed {
        log::info!("🔑 Dev key seed detected, inserting session keys...");
        sp_session::generate_initial_session_keys(
            client.clone(),
            client.info().best_hash,
            vec![seed.clone()],
            keystore.clone(),
        ).map_err(|e| Error::Application(Box::new(e)))?;
        log::info!("✅ Session keys generated successfully");
    } else {
        log::warn!("⚠️ No dev key seed found, role: {:?}", config.role);
    }

    // Log BABE configuration from runtime API
    let best_hash = client.info().best_hash;
    let babe_config_result = client.runtime_api().configuration(best_hash);
    match babe_config_result {
        Ok(cfg) => {
            log::info!("📋 BABE config: slot_duration={}ms, authorities={}, epoch_length={}",
                cfg.slot_duration, cfg.authorities.len(), cfg.epoch_length);
        }
        Err(e) => {
            log::error!("❌ Failed to get BABE config: {:?}", e);
        }
    }"""

new_block = """    // Manually insert dev keys into keystore for development chain
    if config.role.is_authority()
        && config.chain_spec.chain_type() == sc_chain_spec::ChainType::Development
    {
        log::info!("🔑 Inserting Alice dev keys into keystore...");

        // Insert Alice's Sr25519 key for BABE
        let alice = Sr25519Keyring::Alice;
        let babe_pair = alice.pair();
        let babe_public = babe_pair.public();
        Keystore::insert(&*keystore_container.local_keystore(),
            sp_consensus_babe::app::Public::ID,
            &babe_pair.to_raw_vec(),
        ).map_err(|e| Error::Application(Box::new(e)))?;
        log::info!("✅ BABE key inserted: {:?}", babe_public);

        // Insert Alice's Ed25519 key for GRANDPA
        use sp_keyring::Ed25519Keyring;
        let alice_ed = Ed25519Keyring::Alice;
        let grandpa_pair = alice_ed.pair();
        Keystore::insert(&*keystore_container.local_keystore(),
            sp_consensus_grandpa::app::Public::ID,
            &grandpa_pair.to_raw_vec(),
        ).map_err(|e| Error::Application(Box::new(e)))?;
        log::info!("✅ GRANDPA key inserted: {:?}", grandpa_pair.public());

        // Also insert Alice's Sr25519 key for account/transactions
        Keystore::insert(&*keystore_container.local_keystore(),
            sp_runtime::traits::IdentifyAccount::ID,
            &babe_pair.to_raw_vec(),
        ).map_err(|e| Error::Application(Box::new(e)))?;
        log::info!("✅ Account key inserted");
    }

    // Log BABE configuration from runtime API
    let best_hash = client.info().best_hash;
    let babe_config_result = client.runtime_api().configuration(best_hash);
    match babe_config_result {
        Ok(cfg) => {
            log::info!("📋 BABE config: slot_duration={}ms, authorities={}, epoch_length={}",
                cfg.slot_duration, cfg.authorities.len(), cfg.epoch_length);
        }
        Err(e) => {
            log::error!("❌ Failed to get BABE config: {:?}", e);
        }
    }"""

content = content.replace(old_block, new_block)

with open("/dev/stdout", "w") as f:
    f.write(content)
