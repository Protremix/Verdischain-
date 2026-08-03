import sys

with open(sys.argv[1], "r") as f:
    content = f.read()

# Add keystore key inspection after session key generation
old = '''        log::info!("Session keys generated");
    }'''

new = '''        log::info!("Session keys generated");

        // Check what keys are in the keystore
        let babe_keys = sp_keystore::Keystore::keys(
            &*keystore,
            sp_consensus_babe::KEY_TYPE,
        ).unwrap_or_default();
        log::info!("BABE keys in keystore: {}", babe_keys.len());
        for k in &babe_keys {
            log::info!("  BABE key: {:x?}", k);
        }

        let grandpa_keys = sp_keystore::Keystore::keys(
            &*keystore,
            sp_consensus_grandpa::KEY_TYPE,
        ).unwrap_or_default();
        log::info!("GRANDPA keys in keystore: {}", grandpa_keys.len());
        for k in &grandpa_keys {
            log::info!("  GRANDPA key: {:x?}", k);
        }
    }'''

content = content.replace(old, new)

# Also log BABE authorities
old_config = '''    if let Ok(cfg) = client.runtime_api().configuration(best_hash) {
        log::info!("BABE: slot={}ms auth={} epoch={}",
            cfg.slot_duration, cfg.authorities.len(), cfg.epoch_length);
    }'''

new_config = '''    if let Ok(cfg) = client.runtime_api().configuration(best_hash) {
        log::info!("BABE: slot={}ms auth={} epoch={}",
            cfg.slot_duration, cfg.authorities.len(), cfg.epoch_length);
        for auth in &cfg.authorities {
            log::info!("  BABE authority: {}", auth.0);
        }
    }'''

content = content.replace(old_config, new_config)

with open(sys.argv[1], "w") as f:
    f.write(content)
print("OK")
