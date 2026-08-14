# Architectural Decisions — Partial Pallets

**Date:** 2026-08-14
**Status:** Approved by engineering review

## M2: Solana-Inspired Pallets

**Decision:** The 6 Solana-inspired pallets (PoH, GulfStream, Turbine, ZkCompression, ALT, Sealevel) are included in the runtime as optional capability layers, not as consensus-critical components.

**Rationale:**
- Substrate consensus is BABE/GRANDPA — these pallets do NOT replace it
- They provide on-chain state and logic activatable via runtime upgrades
- Sealevel (parallel smart contract execution): 11/11 E2E tests PASS
- Circuit breaker integration exists for emergency pausing

**Mainnet impact:** NONE. These pallets add storage and extrinsics but do not affect block production, finality, or consensus. Inert until explicitly called.

## M3: IBC (Inter-Blockchain Communication)

**Decision:** IBC is implemented as a foundation layer (Phase 1 complete). Full cross-chain communication (Phase 2) is post-testnet.

**Rationale:**
- Phase 1: ChannelEnd, client management, packet structures — 28 tests PASS
- Phase 2: Light client verification, relayer, end-to-end handshake — planned
- IBC pallet provides the on-chain protocol surface for future cross-chain bridging
- Not required for mainnet launch — Verdis Chain operates standalone

**Mainnet impact:** NONE. IBC pallet is inert until a relayer is connected and a light client is registered.

## Conclusion

Both M2 and M3 are architectural decisions, not defects. Neither blocks mainnet launch.
