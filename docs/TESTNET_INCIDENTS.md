# Verdis Chain Testnet Incident Log

## Incident #001 — Finality Stuck at Block #0
**Date:** 2026-08-14 (pre-fix)  
**Severity:** Critical  
**Description:** GRANDPA finality was stuck at block #0. Blocks were being produced by BABE but not finalized.  
**Root Cause:** Session keys were only generated for 3 of 6 validators. The Session pallet could not load keys for the other 3, causing GRANDPA to stall.  
**Resolution:** Fixed `build_session_keys` to generate keys for all validators. Reverted `validator_count` to 3 to match running nodes.  
**Status:** RESOLVED  

## Incident #002 — Chain Spec File Corruption
**Date:** 2026-08-14 12:57 UTC  
**Severity:** High  
**Description:** Chain spec file `testnet-canonical-raw.json` was corrupted — started with a timestamp instead of JSON.  
**Root Cause:** `build-spec` command output log messages to stdout before JSON. Stderr was not redirected.  
**Resolution:** Regenerated with `2>/dev/null` to suppress stderr.  
**Status:** RESOLVED  

## Incident #003 — Node2/Node3 Crash on Invalid Chain Spec
**Date:** 2026-08-14 12:59 UTC  
**Severity:** High  
**Description:** Node2 and Node3 crashed with "invalid type: integer 2026, expected struct ClientSpec".  
**Root Cause:** Chain spec file contained log output instead of valid JSON (see Incident #002).  
**Resolution:** Regenerated valid chain spec, purged all chain data, restarted nodes.  
**Status:** RESOLVED  

## Incident #004 — Block Production Stuck at #0 After Regeneration
**Date:** 2026-08-14 13:03 UTC  
**Severity:** Critical  
**Description:** After regenerating chain spec with 6 session keys and validator_count=6, block production was stuck at #0.  
**Root Cause:** With 6 active validators but only 3 running nodes, GRANDPA needed 5/6 votes but could only get 3.  
**Resolution:** Reverted validator_count to 3, restored working chain spec from previous commit.  
**Status:** RESOLVED  

## Incident #005 — Session Key Loading Errors (36 errors)
**Date:** 2026-08-14 (pre-fix)  
**Severity:** Medium  
**Description:** 36 "failed to load session key" errors in node logs.  
**Root Cause:** Chain spec had 21 DPoS validators but only 3 session keys. The 18 validators without keys were skipped.  
**Resolution:** Restored chain spec with 3 active validators (all with keys). Standby validators without keys are expected.  
**Status:** RESOLVED (warnings reduced to 0 for active validators)  

---

## Incident Reporting Template

```
## Incident #XXX — [Title]
**Date:** YYYY-MM-DD HH:MM UTC
**Severity:** Critical / High / Medium / Low
**Description:** [What happened]
**Root Cause:** [Why it happened]
**Resolution:** [How it was fixed]
**Status:** RESOLVED / OPEN / MONITORING
```
