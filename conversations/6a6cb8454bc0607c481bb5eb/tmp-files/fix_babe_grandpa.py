import sys

with open(sys.argv[1], "r") as f:
    content = f.read()

# Fix 1: Add SlotProportion import
old_imports = "use sc_consensus_babe::{self, BabeParams, ImportQueueParams};"
new_imports = "use sc_consensus_babe::{self, BabeParams, ImportQueueParams, SlotProportion};"
content = content.replace(old_imports, new_imports)

# Fix 2: BabeParams - change justification_import to justification_sync_link and fix block_proposal_slot_portion
old_babe = """        let babe_worker = sc_consensus_babe::start_babe(
            BabeParams {
                keystore: keystore.clone(),
                client: client.clone(),
                select_chain: select_chain.clone(),
                env: proposer_factory,
                block_import: babe_block_import,
                sync_oracle: sync_service.clone(),
                justification_import: None,
                create_inherent_data_providers: move |_, ()| {
                    let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
                    let slot = sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                        *timestamp,
                        sp_consensus_babe::SlotDuration::from_millis(6000),
                    );
                    async move { Ok((slot, timestamp)) }
                },
                force_authoring: false,
                backoff_authoring_blocks: None,
                babe_link: babe_link.clone(),
                block_proposal_slot_portion: None,
                max_block_proposal_slot_portion: None,
                telemetry: None,
            },
        ).map_err(|e| Error::Application(Box::new(e)))?;"""

new_babe = """        let babe_worker = sc_consensus_babe::start_babe(
            BabeParams {
                keystore: keystore.clone(),
                client: client.clone(),
                select_chain: select_chain.clone(),
                env: proposer_factory,
                block_import: babe_block_import,
                sync_oracle: sync_service.clone(),
                justification_sync_link: (),
                create_inherent_data_providers: move |_, ()| {
                    let timestamp = sp_timestamp::InherentDataProvider::from_system_time();
                    let slot = sp_consensus_babe::inherents::InherentDataProvider::from_timestamp_and_slot_duration(
                        *timestamp,
                        sp_consensus_babe::SlotDuration::from_millis(6000),
                    );
                    async move { Ok((slot, timestamp)) }
                },
                force_authoring: false,
                backoff_authoring_blocks: None,
                babe_link: babe_link.clone(),
                block_proposal_slot_portion: SlotProportion::new(0.5),
                max_block_proposal_slot_portion: None,
                telemetry: None,
            },
        ).map_err(|e| Error::Application(Box::new(e)))?;"""

content = content.replace(old_babe, new_babe)

# Fix 3: run_voter -> run_grandpa_voter
content = content.replace("sc_consensus_grandpa::run_voter", "sc_consensus_grandpa::run_grandpa_voter")

with open(sys.argv[1], "w") as f:
    f.write(content)
print("OK")
