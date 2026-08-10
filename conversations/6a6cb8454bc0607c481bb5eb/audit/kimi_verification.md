**Assumption:** ratings below treat each finding *as described* in the audit. Where source/config context is required to confirm, I’ve marked `NEEDS_INVESTIGATION`.

## Cross-Verification Ratings

| # | Pallet | Finding | Rating | Rationale |
|---|--------|---------|--------|-----------|
| 1 | DPoS | Unbounded `Votes::iter()` in `do_slash` | **CONFIRMED** | Unbounded iteration in a dispatchable = unbounded weight / DoS risk. |
| 2 | DPoS | Wrong slash fraction: division before multiplication | **CONFIRMED** | Truncates early; can produce zero or wrong slash amounts. |
| 3 | DPoS | `slash_validator` wrong unreserve semantics | **CONFIRMED** | Likely slashes free balance instead of reserved, under-/over-slashing. |
| 4 | DPoS | `reactivate_validator` overflow (`block + cooldown` as u32) | **CONFIRMED** | Primitive u32 addition can wrap/panic; cooldown should be checked/saturating. |
| 5 | DPoS | `reward_block_producer` missing authorization | **CONFIRMED** | Anyone minting rewards to arbitrary validators = inflation/theft. |
| 6 | DPoS | `SlashingEvents` counter overflow | **CONFIRMED** | `*c += 1` on a fixed-width type can wrap; use `saturating_add` or `checked_add`. |
| 7 | DPoS | `TotalStaked` underflow with capped slash | **CONFIRMED** | `saturating_sub` avoids underflow, but state becomes inconsistent if slash failed. |
| 8 | DPoS | Non-atomic state in `slash_validator` | **CONFIRMED** | Storage mutated before balance transfer; failure leaves inconsistent state. |
| 9 | AMM-DEX | State updated before transfer in swap | **CONFIRMED** | Non-atomic ordering can corrupt pool state if the transfer fails/returns Err. |
| 10 | AMM-DEX | `create_pool` uses `reserve()` instead of `transfer()` | **NEEDS_INVESTIGATION** | `reserve()` can be valid for locking LP funds, but if users can unreserve it becomes a drain. |
| 11 | Presale | Same currency for payment + token | **NEEDS_INVESTIGATION** | Only exploitable if price logic is flawed; same-asset sale is not inherently free money. |
| 12 | Vesting | TOCTOU in `release_vested` (two block-number reads) | **FALSE_POSITIVE** | `frame_system` block number is constant for the whole extrinsic; no TOCTOU. |
| 13 | Vesting | Integer division truncation locks dust | **CONFIRMED** | Per-block vesting can leave unreleasable dust if remainder not handled. |
| 14 | Vesting | `do_assign_vesting` pub, no origin check | **NEEDS_INVESTIGATION** | Name suggests an internal helper; if it is a dispatchable, it is critical. |
| 15 | Tokenomics | `purchase()` collects no payment | **CONFIRMED** | Direct free-token mint if payment is never transferred/burned. |
| 16 | Tokenomics | Arithmetic overflow in cost calculation | **CONFIRMED** | Unchecked integer math; use `checked_mul`/`saturating` patterns. |
| 17 | Tokenomics | Non-atomic state updates enable double-spend | **CONFIRM