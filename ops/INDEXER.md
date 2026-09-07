# Indexer stack

An explorer at Solscan/Etherscan level cannot run on direct RPC calls. A node answers
"give me block N" but never "give me every transfer touching this address" - that requires
the chain decoded once into a relational store. This is that layer.

```
PostgreSQL 18.6     db verdis, 8 tables, 25 indexes, loopback only
verdis-indexer      verdis_indexer.py --follow      9.8 blocks/sec
verdis-index-api    index_api.py on 127.0.0.1:4500  -> /api/v2
```

`/api/v1` (node-backed) is unchanged. `/api/v2` is additive, so the frontend migrates
endpoint by endpoint with no flag day.

## Endpoints the node cannot serve

`/api/v2/status` `/stats` `/blocks` `/block/{n}` `/extrinsics` `/transfers`
`/account/{addr}` `/account/{addr}/transfers` `/account/{addr}/extrinsics`
`/holders` `/producers` `/activity` `/search?q=` `/health`

## Performance: metadata caching is the whole game

The first run managed 1.0 blocks/sec - 15.5 hours for 50k blocks. Profiling each RPC call
per block showed why:

```
get_block_metadata   852.8 ms/block   85.3%
decode_extrinsics     86.9 ms/block    8.7%
get_block_header      24.0 ms/block    2.4%
get_events            18.5 ms/block    1.8%
chain_getBlock        11.4 ms/block    1.1%
```

`get_block_metadata()` refetches and reparses 231 KB for every block. specVersion is
constant (16) at blocks 1 / 10000 / 25000 / 40000 / 50000, so metadata is cached **keyed
by specVersion** - not unconditionally, because a runtime upgrade changes call indices and
decoding old blocks with new metadata produces silently wrong call names.

Result: **9.8 blocks/sec**, full chain in ~76 minutes. Profile before optimising.

## substrate-interface 1.8.1 cannot read this node

`get_block()` passes the RPC's extrinsic field straight into `ScaleBytes`, but this node
returns each extrinsic as a **list of byte values**, not a hex string:

```
ValueError: Provided data is not in supported format: provided '<class 'list'>'
```

It fails on every block including block 1. `get_events()`, `get_block_header()` and the
author lookup are unaffected, so only the extrinsic step is reimplemented: fetch
`chain_getBlock` directly, normalise to hex, decode with per-specVersion metadata.

## Schema rules that prevent silent corruption

- Balances are `NUMERIC(39,0)`, never `BIGINT`. VRDX has 9 decimals and 100 billion
  issuance = 1e20 planck; int64 caps at 9.2e18, so BIGINT truncates silently.
- The API returns u128 amounts as **strings**; a JSON number at 1e20 loses precision in
  JavaScript.
- `accounts.free` comes from a storage read, never from summing transfers - fees, staking
  and rewards move funds without a Transfer event, so a running total drifts permanently.
- Natural primary keys plus `ON CONFLICT` make re-processing a block a no-op: a crash
  costs nothing and a restart never re-indexes from genesis.
- Genesis is verified against `indexer_state` before the first write. Pointing the indexer
  at a second chain would interleave two histories.

## Monitoring: check progress, not liveness

A stalled indexer keeps every page returning HTTP 200 while the data silently ages.
`mainnet_health.sh` compares `last_indexed_block` with the previous run's position and
raises CRIT only when it is >20 behind AND has not advanced - a backfill is legitimately
tens of thousands of blocks behind and must not alarm.

## Measured: mainnet has no user transactions

`measure_chain_activity.py` sampled 1001 blocks across three independent windows (last
300, first 300 after genesis, 400 random):

```
blocks sampled            1001
with >1 extrinsic            0    (every block carries only Timestamp.set)
Balances.Transfer events     0 / 121 blocks checked
System.Account keys         33
total issuance             100,000,003,000 VRDX
```

The chain produces and finalizes correctly - 21 authorities, finality lag 3, block authors
evenly distributed at 9.4-10.9% each - but nothing transacts on it. The explorer therefore
shows empty transaction, holder and volume views. That is not an indexer defect and must
not be papered over with synthetic data.

90 of the 100 billion VRDX sit on `modl*` PalletId accounts, which have no private key by
construction. The rich list excludes them by default: counting them as holders
misrepresents distribution.

## Credentials

Database credentials live only in `/etc/verdis/indexer.env` (mode 600) on the server and
are read from the environment. No credential appears in this repository.
