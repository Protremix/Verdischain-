#!/usr/bin/env bash
# Is the validator set ELECTED (stake-based, Staking/Dpos) or FIXED (genesis list)?
#
# This decides everything about the "6 lost keys" question:
#   * If the set is elected each era, we do NOT need the 6 lost keys and we do NOT
#     need Council. We can register NEW validators with fresh session keys, bond
#     stake, and the set rotates to include them - shrinking or replacing the idle
#     authorities automatically.
#   * If the set is fixed in genesis and only changeable by sudo/governance, then
#     with no Sudo pallet and no Council keys we are genuinely stuck at 15/21.
#
# Read-only.

KEY=$HOME/.ssh/id_ed25519
SSH="ssh -o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i $KEY"

$SSH root@185.84.224.91 'bash -s' <<'REMOTE' 2>&1
R() { curl -s -m 12 -H 'Content-Type: application/json' \
      -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$1\",\"params\":$2}" http://localhost:9944; }

echo "=== 1. Session.Validators (who signs right now) ==="
SV=$(R state_getStorage '["0xcec5070d609dd3497f72bde07fc96ba088dcde934c658227ee1dfafcd6e16903"]' | grep -oP 'result":"0x\K[0-9a-f]+')
if [ -n "$SV" ]; then
  # compact prefix then 32-byte AccountIds
  n=$(( ${#SV} / 64 ))
  echo "  hex length ${#SV} -> approx $n accounts (32 bytes each)"
else
  echo "  empty/absent"
fi

echo
echo "=== 2. Staking: is anyone actually staking? ==="
# Staking.ValidatorCount
VC=$(R state_getStorage '["0x5f3e4907f716ac89b6347d15ececedca0b6a45321efae92aea15e0740ec7afe7"]' | grep -oP 'result":"0x\K[0-9a-f]+')
echo "  Staking.ValidatorCount raw: ${VC:-absent}"
if [ -n "$VC" ]; then
  # u32 little-endian
  b=$(echo "$VC" | cut -c1-8)
  dec=$(( 0x${b:6:2}${b:4:2}${b:2:2}${b:0:2} ))
  echo "  -> desired validator count: $dec"
fi

# Staking.CurrentEra
CE=$(R state_getStorage '["0x5f3e4907f716ac89b6347d15ececedca487df464e44a534ba6b0cbb32407b587"]' | grep -oP 'result":"0x\K[0-9a-f]+')
echo "  Staking.CurrentEra raw: ${CE:-absent}"

# Staking.Validators map - count entries
echo
echo "=== 3. how many accounts registered as validators via Staking? ==="
KEYS=$(R state_getKeysPaged '["0x5f3e4907f716ac89b6347d15ececedca9220e172bed316605f73f1ff7b4ade98b",500,"0x5f3e4907f716ac89b6347d15ececedca9220e172bed316605f73f1ff7b4ade98b"]')
CNT=$(echo "$KEYS" | grep -oP '0x[0-9a-f]{80,}' | wc -l)
echo "  Staking.Validators entries: $CNT"

echo
echo "=== 4. Dpos pallet storage (custom pallet - may drive the set) ==="
for name in Validators ValidatorCount CandidatePool Candidates SelectedCandidates TotalStake; do
  echo "  probing Dpos.$name"
done
echo "  (need metadata to compute keys - see step 6)"

echo
echo "=== 5. Session.QueuedKeys - does the set change next session? ==="
QK=$(R state_getStorage '["0xcec5070d609dd3497f72bde07fc96ba0f7d5b7d43a1fdd1c4e2e39a9c2f0e0a4"]' | head -c 100)
echo "  ${QK:-absent}"

echo
echo "=== 6. which pallets expose set-changing calls? ==="
M=$(R state_getMetadata '[]')
echo "  metadata: $(echo -n "$M" | wc -c) bytes"
for call in set_keys purge_keys bond validate nominate chill set_validator_count \
            increase_validator_count force_new_era set_invulnerables join_candidates \
            leave_candidates candidate_bond_more set_authorities note_stalled; do
  H=$(printf "%s" "$call" | xxd -p | tr -d '\n')
  echo "$M" | grep -qi "$H" && echo "    call present: $call"
done
REMOTE
