-- Verdis Chain indexer schema
--
-- Purpose: an explorer at Solscan/Etherscan level cannot be built on direct RPC calls.
-- A node answers "give me block N" but never "give me every transfer touching this
-- address" - that requires the chain to be decoded once and stored relationally.
-- This schema is what turns 50k blocks of SCALE blobs into queryable history.
--
-- Design notes that matter for correctness:
--
--  * Amounts are NUMERIC(39,0), not BIGINT. Substrate balances are u128; VRDX has
--    9 decimals and 100 billion issuance = 1e20 planck, which overflows int64
--    (max ~9.2e18). Storing balances as BIGINT would silently corrupt values.
--    NUMERIC(39,0) holds the full u128 range (max ~3.4e38).
--  * Block hashes and addresses are TEXT, not BYTEA: they are compared and displayed
--    as hex/ss58 constantly, and TEXT keeps queries and the API honest and readable.
--  * Every table that the UI paginates has an index on its sort key. An explorer's
--    default view is "latest N", so DESC indexes on block_number/timestamp are what
--    keep those queries at a few milliseconds instead of a sequential scan.
--  * transfers is deliberately denormalised out of events: "account history" is the
--    single hottest query in any explorer and must not require decoding event args
--    at read time.
--  * indexer_state exists so the indexer is resumable and idempotent. A crash must
--    never mean re-indexing from genesis, and re-processing a block must not
--    duplicate rows - hence natural primary keys (block_number, extrinsic_index).

CREATE TABLE IF NOT EXISTS blocks (
    number          BIGINT PRIMARY KEY,
    hash            TEXT NOT NULL UNIQUE,
    parent_hash     TEXT NOT NULL,
    state_root      TEXT,
    extrinsics_root TEXT,
    timestamp       TIMESTAMPTZ,
    author          TEXT,                  -- block producer (BABE), ss58
    extrinsic_count INT NOT NULL DEFAULT 0,
    event_count     INT NOT NULL DEFAULT 0,
    transfer_count  INT NOT NULL DEFAULT 0,
    finalized       BOOLEAN NOT NULL DEFAULT FALSE,
    spec_version    INT,
    indexed_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS blocks_ts_idx        ON blocks (timestamp DESC);
CREATE INDEX IF NOT EXISTS blocks_author_idx    ON blocks (author);
CREATE INDEX IF NOT EXISTS blocks_finalized_idx ON blocks (finalized) WHERE NOT finalized;

CREATE TABLE IF NOT EXISTS extrinsics (
    block_number    BIGINT NOT NULL REFERENCES blocks(number) ON DELETE CASCADE,
    idx             INT NOT NULL,          -- index within the block
    hash            TEXT,
    signer          TEXT,                  -- ss58, NULL for inherents
    call_module     TEXT NOT NULL,
    call_function   TEXT NOT NULL,
    args            JSONB,
    success         BOOLEAN,
    fee             NUMERIC(39,0),
    nonce           BIGINT,
    tip             NUMERIC(39,0),
    signed          BOOLEAN NOT NULL DEFAULT FALSE,
    timestamp       TIMESTAMPTZ,
    PRIMARY KEY (block_number, idx)
);
CREATE INDEX IF NOT EXISTS extrinsics_signer_idx ON extrinsics (signer, block_number DESC);
CREATE INDEX IF NOT EXISTS extrinsics_call_idx   ON extrinsics (call_module, call_function);
CREATE INDEX IF NOT EXISTS extrinsics_hash_idx   ON extrinsics (hash);
CREATE INDEX IF NOT EXISTS extrinsics_block_idx  ON extrinsics (block_number DESC);

CREATE TABLE IF NOT EXISTS events (
    block_number    BIGINT NOT NULL REFERENCES blocks(number) ON DELETE CASCADE,
    idx             INT NOT NULL,          -- index within the block
    extrinsic_idx   INT,                   -- NULL for on-initialize/finalize events
    module          TEXT NOT NULL,
    event           TEXT NOT NULL,
    attributes      JSONB,
    timestamp       TIMESTAMPTZ,
    PRIMARY KEY (block_number, idx)
);
CREATE INDEX IF NOT EXISTS events_module_idx ON events (module, event, block_number DESC);
CREATE INDEX IF NOT EXISTS events_block_idx  ON events (block_number DESC);

-- The hottest table in the explorer: account history.
CREATE TABLE IF NOT EXISTS transfers (
    id              BIGSERIAL PRIMARY KEY,
    block_number    BIGINT NOT NULL REFERENCES blocks(number) ON DELETE CASCADE,
    extrinsic_idx   INT,
    event_idx       INT NOT NULL,
    from_address    TEXT,
    to_address      TEXT,
    amount          NUMERIC(39,0) NOT NULL,
    fee             NUMERIC(39,0),
    success         BOOLEAN NOT NULL DEFAULT TRUE,
    timestamp       TIMESTAMPTZ,
    UNIQUE (block_number, event_idx)
);
CREATE INDEX IF NOT EXISTS transfers_from_idx  ON transfers (from_address, block_number DESC);
CREATE INDEX IF NOT EXISTS transfers_to_idx    ON transfers (to_address, block_number DESC);
CREATE INDEX IF NOT EXISTS transfers_block_idx ON transfers (block_number DESC);
CREATE INDEX IF NOT EXISTS transfers_ts_idx    ON transfers (timestamp DESC);

-- Rolling account state. free/reserved come from a storage read, not from summing
-- transfers: summing is wrong the moment staking, fees or rewards move funds.
CREATE TABLE IF NOT EXISTS accounts (
    address         TEXT PRIMARY KEY,
    free            NUMERIC(39,0),
    reserved        NUMERIC(39,0),
    frozen          NUMERIC(39,0),
    nonce           BIGINT,
    is_validator    BOOLEAN NOT NULL DEFAULT FALSE,
    is_pallet       BOOLEAN NOT NULL DEFAULT FALSE,   -- modl* PalletId account
    first_seen      BIGINT,                            -- block number
    last_activity   BIGINT,
    tx_count        BIGINT NOT NULL DEFAULT 0,
    transfer_count  BIGINT NOT NULL DEFAULT 0,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS accounts_free_idx     ON accounts (free DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS accounts_activity_idx ON accounts (last_activity DESC);

CREATE TABLE IF NOT EXISTS validators (
    address         TEXT PRIMARY KEY,
    name            TEXT,
    stake           NUMERIC(39,0),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    blocks_produced BIGINT NOT NULL DEFAULT 0,
    last_block      BIGINT,
    green_score     INT,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Resumability. One row per network so the same schema can serve mainnet/testnet.
CREATE TABLE IF NOT EXISTS indexer_state (
    network             TEXT PRIMARY KEY,
    genesis_hash        TEXT NOT NULL,     -- guards against pointing at another chain
    last_indexed_block  BIGINT NOT NULL DEFAULT -1,
    last_finalized      BIGINT NOT NULL DEFAULT -1,
    chain_tip           BIGINT,
    blocks_indexed      BIGINT NOT NULL DEFAULT 0,
    started_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_error          TEXT
);

-- Per-day rollups so charts do not aggregate millions of rows on every page load.
CREATE TABLE IF NOT EXISTS daily_stats (
    day             DATE PRIMARY KEY,
    blocks          BIGINT NOT NULL DEFAULT 0,
    extrinsics      BIGINT NOT NULL DEFAULT 0,
    transfers       BIGINT NOT NULL DEFAULT 0,
    volume          NUMERIC(39,0) NOT NULL DEFAULT 0,
    fees            NUMERIC(39,0) NOT NULL DEFAULT 0,
    active_accounts BIGINT NOT NULL DEFAULT 0,
    new_accounts    BIGINT NOT NULL DEFAULT 0
);
