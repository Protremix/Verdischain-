#!/usr/bin/env bash
# Verdis Chain Security Audit Scanner
# Comprehensive Substrate/Rust blockchain security scanner
# Usage: scan.sh <full|quick|access|arithmetic|secrets|reentrancy|economic|storage|infrastructure|deps|genesis|rpc> <project_path>

set -euo pipefail

SCAN_TYPE="${1:-full}"
PROJECT_PATH="${2:-/opt/verdis-chain-rust}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# Counters
CRITICAL=0
HIGH=0
MEDIUM=0
LOW=0
TOTAL=0

# Report file
REPORT_FILE="/tmp/verdis-security-report-$(date +%Y%m%d-%H%M%S).md"

echo "# Verdis Chain Security Audit Report" > "$REPORT_FILE"
echo "**Date:** $(date -u '+%Y-%m-%d %H:%M UTC')" >> "$REPORT_FILE"
echo "**Scanner:** verdis-security-audit v1.0" >> "$REPORT_FILE"
echo "**Target:** $PROJECT_PATH" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Helper: add finding to report
add_finding() {
    local severity="$1"
    local scanner="$2"
    local file="$3"
    local line="$4"
    local title="$5"
    local detail="$6"
    local remediation="$7"

    TOTAL=$((TOTAL + 1))
    case "$severity" in
        CRITICAL) CRITICAL=$((CRITICAL + 1)) ;;
        HIGH) HIGH=$((HIGH + 1)) ;;
        MEDIUM) MEDIUM=$((MEDIUM + 1)) ;;
        LOW) LOW=$((LOW + 1)) ;;
    esac

    echo -e "${RED}${BOLD}[$severity]${NC} $title"
    echo -e "  ${CYAN}File:${NC} $file:$line"
    echo -e "  ${YELLOW}Detail:${NC} $detail"
    echo -e "  ${GREEN}Fix:${NC} $remediation"
    echo ""

    echo "### [$severity] $title" >> "$REPORT_FILE"
    echo "- **Scanner:** $scanner" >> "$REPORT_FILE"
    echo "- **File:** \`$file:$line\`" >> "$REPORT_FILE"
    echo "- **Detail:** $detail" >> "$REPORT_FILE"
    echo "- **Remediation:** $remediation" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

# Helper: add info to report
add_info() {
    local scanner="$1"
    local message="$2"
    echo -e "${CYAN}[INFO]${NC} $message"
    echo "- $message" >> "$REPORT_FILE"
}

# ============ SCANNER: ACCESS CONTROL ============
scan_access() {
    echo -e "${BOLD}${MAGENTA}=== Access Control Audit ===${NC}"
    echo "## Access Control Audit" >> "$REPORT_FILE"

    local pallets_dir="$PROJECT_PATH/pallets"
    if [ ! -d "$pallets_dir" ]; then
        add_info "access" "No pallets directory found at $pallets_dir"
        return
    fi

    # Find all ensure_signed calls — these should be reviewed for privilege
    local signed_fns=$(grep -rn "ensure_signed" "$pallets_dir" --include="*.rs" | grep -v "test" | grep -v "benchmark" | grep -v "#\[cfg")

    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)

        # Check if this function handles value transfers or privileged operations
        local fn_context=$(sed -n "$((line_no > 10 ? line_no - 10 : 1)),$((line_no + 20))p" "$file")

        if echo "$fn_context" | grep -qi "transfer\|mint\|burn\|slash\|reward\|withdraw\|set.*score\|update.*config\|register_validator\|create_pool\|add_liquidity"; then
            add_finding "HIGH" "access" "$file" "$line_no" \
                "Privileged operation uses ensure_signed instead of ensure_root" \
                "Function near this line handles sensitive operations (transfer/mint/slash/reward) but uses ensure_signed, allowing any account to call it" \
                "Review if this should be ensure_root or add a role/council check. If user-initiated is intended, add proper authorization checks (e.g., only the account owner)"
        fi
    done <<< "$signed_fns"

    # Check for missing origin checks
    local missing_origin=$(grep -rn "pub fn " "$pallets_dir" --include="*.rs" | grep -v "test" | grep -v "benchmark" | grep -v "fn dispatch" | while read -r match; do
        local file=$(echo "$match" | cut -d: -f1)
        local line_no=$(echo "$match" | cut -d: -f2)
        local fn_line=$(sed -n "${line_no},$((line_no + 5))p" "$file")
        if ! echo "$fn_line" | grep -q "origin\|OriginFor"; then
            echo "$match"
        fi
    done)

    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)
        local fn_name=$(echo "$line_match" | grep -oP "pub fn \K\w+")

        # Skip helper functions, getters, internal functions
        if echo "$fn_name" | grep -qi "get\|calculate\|compute\|estimate\|check\|validate\|do_\|inner\|_impl"; then
            continue
        fi

        add_finding "MEDIUM" "access" "$file" "$line_no" \
            "Extrinsic '$fn_name' may lack origin check" \
                "Public function does not appear to take an origin parameter — it may be callable without authorization" \
                "Ensure all extrinsics take origin and call ensure_signed/ensure_root. Internal helpers should be private (fn, not pub fn)"
    done <<< "$missing_origin"

    # Check for self-scoring / self-delegation patterns
    local self_calls=$(grep -rn "ensure_signed" "$pallets_dir" --include="*.rs" -A2 | grep -v test | grep -v benchmark | grep -i "self\|who\|caller.*score\|caller.*stake\|caller.*validator")
    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)
        add_finding "HIGH" "access" "$file" "$line_no" \
            "Self-scoring or self-delegation pattern detected" \
                "A function allows the caller to set their own score/stake/validator status — this can be abused for free reputation" \
                "Separate the caller from the target: require ensure_root or a council vote for score assignment"
    done <<< "$self_calls"

    add_info "access" "Access control audit complete"
}

# ============ SCANNER: ARITHMETIC ============
scan_arithmetic() {
    echo -e "${BOLD}${MAGENTA}=== Arithmetic Safety Audit ===${NC}"
    echo "## Arithmetic Safety Audit" >> "$REPORT_FILE"

    local pallets_dir="$PROJECT_PATH/pallets"

    # Find unsafe casts
    local unsafe_casts=$(grep -rn " as u32\| as u64\| as usize\| as u128\| as i32\| as i64\| as i128" "$pallets_dir" --include="*.rs" | grep -v test | grep -v benchmark | grep -v "#\[cfg")

    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)
        local content=$(echo "$line_match" | cut -d: -f3)

        # Check if try_from is already used nearby
        if echo "$content" | grep -q "try_from\|TryFrom\|TryInto"; then
            continue
        fi

        # Check if it's in a saturating context
        if echo "$content" | grep -q "saturating\|checked\|min\|max"; then
            continue
        fi

        add_finding "MEDIUM" "arithmetic" "$file" "$line_no" \
            "Unsafe integer cast" \
                "Direct cast '$content' without bounds checking — can truncate or wrap on large values" \
                "Use try_from/try_into or add explicit bounds checks before casting"
    done <<< "$unsafe_casts"

    # Find saturating arithmetic that should be checked
    local saturating=$(grep -rn "saturating_add\|saturating_sub\|saturating_mul" "$pallets_dir" --include="*.rs" | grep -v test | grep -v benchmark)

    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)

        # Check if this is financial code
        local context=$(sed -n "$((line_no > 5 ? line_no - 5 : 1)),$((line_no + 5))p" "$file")
        if echo "$context" | grep -qi "balance\|amount\|stake\|reward\|pool\|reserve\|liquidity\|transfer\|mint\|burn"; then
            add_finding "MEDIUM" "arithmetic" "$file" "$line_no" \
                "Saturating arithmetic in financial context" \
                    "Saturating arithmetic silently caps at MAX/MIN instead of erroring — in financial code this can cause silent accounting errors" \
                    "Use checked_add/checked_sub/checked_mul with proper error propagation for financial operations"
        fi
    done <<< "$saturating"

    # Find division without zero check
    local divisions=$(grep -rn " / " "$pallets_dir" --include="*.rs" | grep -v test | grep -v benchmark | grep -v "//" | grep -v "*/")
    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)

        # Check if there's a zero check nearby
        local context=$(sed -n "$((line_no > 3 ? line_no - 3 : 1)),$((line_no + 3))p" "$file")
        if echo "$context" | grep -qi "ensure.*> 0\|ensure!.*!.*0\|if.*== 0\|!= 0\|is_zero\|defensive"; then
            continue
        fi

        if echo "$context" | grep -qi "balance\|amount\|stake\|reward\|pool\|reserve\|price\|rate\|ratio\|share"; then
            add_finding "HIGH" "arithmetic" "$file" "$line_no" \
                "Division without zero check in financial context" \
                    "Division operation in financial code without explicit zero-check — can panic on zero denominator" \
                    "Add ensure!(denominator > 0) before division or use checked_div with error handling"
        fi
    done <<< "$divisions"

    # Find unchecked unwrap in production code
    local unwraps=$(grep -rn "\.unwrap()" "$pallets_dir" --include="*.rs" | grep -v test | grep -v benchmark | grep -v "#\[cfg")
    local unwrap_count=0
    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)
        unwrap_count=$((unwrap_count + 1))

        if [ $unwrap_count -le 20 ]; then
            add_finding "LOW" "arithmetic" "$file" "$line_no" \
                "unwrap() in production code" \
                    "Using unwrap() can panic — in blockchain code this causes a failed extrinsic and potential DoS" \
                    "Use ok_or(Error::...)? or unwrap_or_default() instead"
        fi
    done <<< "$unwraps"

    if [ $unwrap_count -gt 20 ]; then
        add_info "arithmetic" "Found $unwrap_count total unwrap() calls (showing first 20)"
    fi

    add_info "arithmetic" "Arithmetic safety audit complete"
}

# ============ SCANNER: SECRETS ============
scan_secrets() {
    echo -e "${BOLD}${MAGENTA}=== Secrets & Hardcoded Keys Audit ===${NC}"
    echo "## Secrets & Hardcoded Keys Audit" >> "$REPORT_FILE"

    # Search for hardcoded private keys, mnemonics, seeds
    local patterns=(
        "0x[0-9a-fA-F]{64}"
        "[0-9a-fA-F]{64}"
        "secret_seed.*=.*\""
        "private_key.*=.*\""
        "mnemonic.*=.*\""
        "SEED.*=.*\""
        "sudo_key.*=.*\""
        "validator_key.*=.*\""
        "session_key.*=.*\""
        "GRANDPA.*=.*\""
        "BABE.*=.*\""
        "aura_secret.*=.*\""
    )

    for pattern in "${patterns[@]}"; do
        local matches=$(grep -rn -E "$pattern" "$PROJECT_PATH" --include="*.rs" --include="*.json" --include="*.toml" --include="*.yaml" --include="*.yml" --include="*.sh" --include="*.py" --include="*.js" --include="*.ts" 2>/dev/null | grep -v target | grep -v node_modules | grep -v ".git" | grep -v test | grep -v "0x0000000000000000000000000000000000000000000000000000000000000000" | grep -v "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")
        while IFS= read -r line_match; do
            [ -z "$line_match" ] && continue
            local file=$(echo "$line_match" | cut -d: -f1)
            local line_no=$(echo "$line_match" | cut -d: -f2)

            # Skip genesis spec hash placeholders
            if echo "$line_match" | grep -qi "code_hash\|wasm_hash\|genesis"; then
                continue
            fi

            add_finding "CRITICAL" "secrets" "$file" "$line_no" \
                "Hardcoded secret detected" \
                    "Potential hardcoded private key, seed, or mnemonic found in source code" \
                    "Remove immediately. Keys should be provided via environment variables or key files, never hardcoded"
        done <<< "$matches"
    done

    # Check for API keys in source
    local api_keys=$(grep -rn "api_key.*=.*\"\|API_KEY.*=.*\"\|token.*=.*\"\|password.*=.*\"" "$PROJECT_PATH" --include="*.rs" --include="*.js" --include="*.py" --include="*.sh" --include="*.ts" --include="*.toml" 2>/dev/null | grep -v target | grep -v node_modules | grep -v ".git" | grep -v ".env" | grep -v test | grep -v "process.env" | grep -v "std::env" | grep -v "getenv" | grep -v "\${" | grep -v "REDACTED")
    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)
        add_finding "CRITICAL" "secrets" "$file" "$line_no" \
            "Hardcoded API key or password" \
                "Credential appears to be hardcoded in source — if committed, it's compromised" \
                "Move to environment variables or .env file (gitignored)"
    done <<< "$api_keys"

    # Check for .env files not gitignored
    if [ -f "$PROJECT_PATH/.env" ]; then
        if ! grep -q ".env" "$PROJECT_PATH/.gitignore" 2>/dev/null; then
            add_finding "HIGH" "secrets" "$PROJECT_PATH/.env" "0" \
                ".env file not in .gitignore" \
                    ".env file exists but .gitignore does not exclude it — secrets may be committed" \
                    "Add .env to .gitignore immediately"
        fi
    fi

    add_info "secrets" "Secrets audit complete"
}

# ============ SCANNER: REENTRANCY ============
scan_reentrancy() {
    echo -e "${BOLD}${MAGENTA}=== Reentrancy & State Audit ===${NC}"
    echo "## Reentrancy & State Audit" >> "$REPORT_FILE"

    local pallets_dir="$PROJECT_PATH/pallets"

    # Substrate reentrancy: state changes after external calls
    # In Substrate, this is mainly about storage writes after callbacks
    local storage_after_call=$(grep -rn "deposit_event\|emit_event" "$pallets_dir" --include="*.rs" -A1 | grep -v test | grep -v benchmark | grep "insert\|put\|set\|swap\|mutate" | head -20)

    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)
        add_finding "LOW" "reentrancy" "$file" "$line_no" \
            "State change after event emission" \
                "Storage modification after event emission — in Substrate this is generally safe but check for external calls between" \
                "Ensure no external calls happen between state reads and writes (CEI pattern: Checks-Effects-Interactions)"
    done <<< "$storage_after_call"

    # Check for unchecked external pallet calls
    local x_calls=$(grep -rn "T::Currency\|T::Balances\|pallet_balances\|pallet_assets" "$pallets_dir" --include="*.rs" | grep -v test | grep -v benchmark | grep -v "use\|import\|mod\|pub" | head -30)

    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)

        # Check if result is handled
        local context=$(sed -n "$((line_no > 2 ? line_no - 2 : 1)),$((line_no + 2))p" "$file")
        if echo "$context" | grep -q "let.*=\|\.map\|\.and_then\|\.ok_or\|?;\|if.*is_some\|if.*is_ok"; then
            continue
        fi

        add_finding "MEDIUM" "reentrancy" "$file" "$line_no" \
            "Cross-pallet call without result handling" \
                "Call to external pallet (Currency/Balances) without explicit error handling" \
                "Use ? operator or explicit match to handle potential errors from cross-pallet calls"
    done <<< "$x_calls"

    add_info "reentrancy" "Reentrancy audit complete"
}

# ============ SCANNER: ECONOMIC ============
scan_economic() {
    echo -e "${BOLD}${MAGENTA}=== Economic Security Audit ===${NC}"
    echo "## Economic Security Audit" >> "$REPORT_FILE"

    local pallets_dir="$PROJECT_PATH/pallets"

    # Check for unbounded rewards
    local rewards=$(grep -rn "reward\|Reward\|mint\|Mint" "$pallets_dir" --include="*.rs" | grep -v test | grep -v benchmark | grep -v "use\|import\|mod\|pub\|Event\|error\|Error")
    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)
        local context=$(sed -n "$((line_no > 5 ? line_no - 5 : 1)),$((line_no + 10))p" "$file")

        if echo "$context" | grep -qi "ensure.*<\|ensure.*max\|ensure.*limit\|ensure.*cap\|ensure.*bounded"; then
            continue
        fi

        if echo "$context" | grep -qi "reward_pool\|RewardPool\|emission\|EmissionRate"; then
            continue
        fi

        if echo "$context" | grep -qi "fn.*reward\|fn.*mint" && ! echo "$context" | grep -qi "ensure\|cap\|limit\|max\|bounded\|pool"; then
            add_finding "HIGH" "economic" "$file" "$line_no" \
                "Reward/mint without upper bound" \
                    "Reward or mint function does not appear to have an upper bound check — could drain treasury or cause inflation" \
                    "Add ensure! checks for max reward per block/epoch, and verify reward pool has sufficient balance"
        fi
    done <<< "$rewards"

    # Check slashing math
    local slashes=$(grep -rn "fn slash\|fn do_slash\|fn penalize\|fn punish" "$pallets_dir" --include="*.rs" | grep -v test | grep -v benchmark)
    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)
        local context=$(sed -n "$((line_no)),$((line_no + 30))p" "$file")

        if ! echo "$context" | grep -qi "ensure.*> 0\|ensure.*penalty\|ensure.*amount\|zero.*penalty\|penalty.*zero"; then
            add_finding "MEDIUM" "economic" "$file" "$line_no" \
                "Slashing without zero-penalty check" \
                    "Slash function may not check for zero penalty — could allow no-op slashes to reset validator status" \
                    "Add ensure!(penalty > 0) to prevent zero-penalty slashing"
        fi

        if echo "$context" | grep -qi "saturating_sub\|saturating"; then
            add_finding "MEDIUM" "economic" "$file" "$line_no" \
                "Slashing uses saturating subtraction" \
                    "Saturating subtraction in slashing silently caps at zero — stake below slash amount loses nothing extra, but accounting may be inconsistent" \
                    "Use checked_sub and handle the case where slash exceeds stake (e.g., remove validator, mark as slashed)"
        fi
    done <<< "$slashes"

    # Check DEX math for standard AMM vulnerabilities
    local dex_files=$(find "$pallets_dir" -name "*.rs" -path "*amm*" -o -name "*.rs" -path "*dex*" | grep -v test)
    for f in $dex_files; do
        # Check for reserve manipulation
        local swaps=$(grep -n "fn swap\|fn do_swap\|fn execute_swap" "$f" | grep -v test)
        while IFS= read -r line_match; do
            [ -z "$line_match" ] && continue
            local line_no=$(echo "$line_match" | cut -d: -f1)
            local context=$(sed -n "${line_no},$((line_no + 40))p" "$f")

            if ! echo "$context" | grep -qi "ensure.*min_out\|ensure.*min_received\|ensure.*slippage\|min_amount"; then
                add_finding "HIGH" "economic" "$f" "$line_no" \
                    "DEX swap without minimum output check" \
                        "Swap function does not check minimum output amount — users can be sandwiched" \
                        "Add min_amount_out parameter and ensure!(amount_out >= min_amount_out) check"
            fi

            if echo "$context" | grep -qi "saturating"; then
                add_finding "MEDIUM" "economic" "$f" "$line_no" \
                    "DEX swap uses saturating arithmetic" \
                        "Saturating arithmetic in DEX can cause silent rounding errors and pool imbalance" \
                        "Use checked arithmetic with proper error propagation"
            fi
        done <<< "$swaps"

        # Check for K invariant
        if ! grep -q "k_last\|K_LAST\|invariant\|reserve_a.*reserve_b\|reserve.*\*.*reserve" "$f" 2>/dev/null; then
            add_finding "LOW" "economic" "$f" "0" \
                "DEX may not enforce constant product invariant" \
                    "No explicit K-invariant check found in DEX pallet" \
                    "Ensure x * y >= k is enforced after every swap"
        fi
    done

    add_info "economic" "Economic security audit complete"
}

# ============ SCANNER: STORAGE ============
scan_storage() {
    echo -e "${BOLD}${MAGENTA}=== Storage Safety Audit ===${NC}"
    echo "## Storage Safety Audit" >> "$REPORT_FILE"

    local pallets_dir="$PROJECT_PATH/pallets"

    # Check for unbounded Vec/Storage
    local unbounded_vec=$(grep -rn "Vec<u8>\|Vec<AccountId>\|Vec<Balance>\|BoundedVec" "$pallets_dir" --include="*.rs" | grep -v test | grep -v benchmark | grep "Storage")
    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)

        if echo "$line_match" | grep -q "BoundedVec"; then
            continue  # BoundedVec is safe
        fi

        if echo "$line_match" | grep -q "Vec<u8>"; then
            add_finding "MEDIUM" "storage" "$file" "$line_no" \
                "Unbounded Vec<u8> in storage" \
                    "Storage uses Vec<u8> without bounds — can grow unboundedly and cause OOM or storage bloat" \
                    "Use BoundedVec<u8, MaxLen> with an appropriate maximum length parameter"
        fi
    done <<< "$unbounded_vec"

    # Check for storage iteration (can be DoS vector)
    local iter_storage=$(grep -rn "iter\(\)\|drain\(\)\|for.*in.*Storage\|for.*in.*Map" "$pallets_dir" --include="*.rs" | grep -v test | grep -v benchmark | grep -v "use\|import")
    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        local file=$(echo "$line_match" | cut -d: -f1)
        local line_no=$(echo "$line_match" | cut -d: -f2)
        add_finding "MEDIUM" "storage" "$file" "$line_no" \
            "Storage iteration in production code" \
                "Iterating over storage maps can be a DoS vector if the map grows large — O(n) operation on chain" \
                "Use bounded iteration with a maximum count, or use pagination/offsets"
    done <<< "$iter_storage"

    # Check for missing StorageMaxValues
    local storage_maps=$(grep -rn "StorageMap\|StorageDoubleMap\|StorageNMap" "$pallets_dir" --include="*.rs" | grep -v test | grep -v benchmark | grep -v "use\|import")
    local map_count=0
    while IFS= read -r line_match; do
        [ -z "$line_match" ] && continue
        map_count=$((map_count + 1))
    done <<< "$storage_maps"
    if [ $map_count -gt 50 ]; then
        add_finding "LOW" "storage" "pallets/" "0" \
            "High number of storage maps ($map_count)" \
                "Large number of storage maps increases prefix collision risk and makes migration harder" \
                "Review if all storage maps are necessary, consider consolidating related data"
    fi

    add_info "storage" "Storage audit complete ($map_count storage maps found)"
}

# ============ SCANNER: INFRASTRUCTURE ============
scan_infrastructure() {
    echo -e "${BOLD}${MAGENTA}=== Infrastructure Security Audit ===${NC}"
    echo "## Infrastructure Security Audit" >> "$REPORT_FILE"

    # Check Docker security
    local dockerfile="$PROJECT_PATH/Dockerfile"
    if [ -f "$dockerfile" ]; then
        if grep -q "USER root\|USER 0" "$dockerfile"; then
            add_finding "HIGH" "infrastructure" "$dockerfile" "0" \
                "Docker runs as root" \
                    "Container runs as root user — privilege escalation risk" \
                    "Add USER 1000 (non-root user) in Dockerfile"
        fi

        if ! grep -q "USER\s\|user:" "$dockerfile"; then
            add_finding "MEDIUM" "infrastructure" "$dockerfile" "0" \
                "Docker USER not specified" \
                    "No USER directive in Dockerfile — defaults to root" \
                    "Add USER directive with a non-root UID"
        fi

        if ! grep -q "read_only\|--read-only\|no-new-privileges" "$dockerfile"; then
            add_finding "LOW" "infrastructure" "$dockerfile" "0" \
                "Docker not read-only" \
                    "Container filesystem is writable — attacker can modify files at runtime" \
                    "Add --read-only flag and mount tmpfs for /tmp"
        fi
    fi

    local compose="$PROJECT_PATH/docker-compose.yml"
    if [ -f "$compose" ]; then
        if grep -q "privileged.*true\|privileged: true" "$compose"; then
            add_finding "CRITICAL" "infrastructure" "$compose" "0" \
                "Docker privileged mode" \
                    "Container runs in privileged mode — full host access" \
                    "Remove privileged: true immediately"
        fi

        if grep -q "ports:.*9933\|ports:.*9934\|ports:.*9944" "$compose"; then
            add_finding "HIGH" "infrastructure" "$compose" "0" \
                "RPC port exposed publicly" \
                    "WebSocket/HTTP RPC port is published to host — anyone can send transactions" \
                    "Bind RPC ports to localhost only (127.0.0.1:9933)"
        fi

        if ! grep -q "cap_drop.*ALL\|cap_drop:.*ALL" "$compose"; then
            add_finding "MEDIUM" "infrastructure" "$compose" "0" \
                "Docker capabilities not dropped" \
                    "Container retains all Linux capabilities — unnecessary attack surface" \
                    "Add cap_drop: [ALL] and only add back what's needed"
        fi
    fi

    # Check nginx config
    local nginx_conf="/etc/nginx/nginx.conf"
    if [ -f "$nginx_conf" ]; then
        if ! grep -q "server_tokens off" "$nginx_conf" 2>/dev/null; then
            add_finding "LOW" "infrastructure" "$nginx_conf" "0" \
                "Nginx server_tokens not off" \
                    "Nginx exposes version number in headers — information leak" \
                    "Add server_tokens off; in http block"
        fi
    fi

    # Check for SSL/TLS config
    local sites_available=$(find /etc/nginx -name "*.conf" 2>/dev/null | head -5)
    for site in $sites_available; do
        if grep -q "listen 80\|listen.*80;" "$site" 2>/dev/null; then
            if ! grep -q "return 301.*https\|redirect.*https" "$site" 2>/dev/null; then
                add_finding "MEDIUM" "infrastructure" "$site" "0" \
                    "HTTP without HTTPS redirect" \
                        "Port 80 is listening without redirecting to HTTPS" \
                        "Add return 301 https://$host$request_uri; for all HTTP listeners"
            fi
        fi
    done

    # Check for open ports
    if command -v ss &>/dev/null; then
        local open_ports=$(ss -tlnp 2>/dev/null | grep -v "127.0.0.1\|::1\|\[::1\]" | grep -v "sshd" | head -10)
        while IFS= read -r port_line; do
            [ -z "$port_line" ] && continue
            local port=$(echo "$port_line" | grep -oP ":\K\d+" | head -1)
            case "$port" in
                30333|30334|30335) ;; # P2P ports should be open
                9933|9934|9944|9945|9946|9949)
                    add_finding "HIGH" "infrastructure" "ss" "0" \
                        "RPC port $port exposed to network" \
                            "RPC port is listening on all interfaces — external access to chain data and potentially signing" \
                            "Bind to 127.0.0.1 only, or use a firewall"
                    ;;
                3000|9090|9100)
                    add_finding "MEDIUM" "infrastructure" "ss" "0" \
                        "Monitoring port $port exposed" \
                            "Monitoring service port (Grafana/Prometheus/Node Exporter) is publicly accessible" \
                            "Bind to localhost only, use SSH tunnel for access"
                    ;;
            esac
        done <<< "$open_ports"
    fi

    # Check SSH config
    local sshd_conf="/etc/ssh/sshd_config"
    if [ -f "$sshd_conf" ]; then
        if grep -qi "PasswordAuthentication yes" "$sshd_conf" 2>/dev/null; then
            add_finding "HIGH" "infrastructure" "$sshd_conf" "0" \
                "SSH password authentication enabled" \
                    "SSH allows password login — brute force risk" \
                    "Set PasswordAuthentication no, use key-based auth only"
        fi

        if grep -qi "PermitRootLogin yes\|PermitRootLogin prohibit-password" "$sshd_conf" 2>/dev/null; then
            if ! grep -qi "PermitRootLogin no" "$sshd_conf"; then
                add_finding "MEDIUM" "infrastructure" "$sshd_conf" "0" \
                    "Root SSH login allowed" \
                        "Root can login via SSH — direct target for attackers" \
                        "Set PermitRootLogin no, use sudo for admin tasks"
                fi
        fi
    fi

    add_info "infrastructure" "Infrastructure audit complete"
}

# ============ SCANNER: DEPENDENCIES ============
scan_deps() {
    echo -e "${BOLD}${MAGENTA}=== Dependency Audit ===${NC}"
    echo "## Dependency Audit" >> "$REPORT_FILE"

    local cargo_lock="$PROJECT_PATH/Cargo.lock"
    if [ ! -f "$cargo_lock" ]; then
        add_info "deps" "No Cargo.lock found"
        return
    fi

    # Check for known vulnerable crate versions (basic check)
    local cargo_file="$PROJECT_PATH/Cargo.toml"
    if [ -f "$cargo_file" ]; then
        # Check for very old Substrate versions
        local substrate_ver=$(grep -oP 'substrate.*version\s*=\s*"\K[^"]+' "$cargo_file" 2>/dev/null | head -1)
        if [ -n "$substrate_ver" ] && [ "$substrate_ver" \< "20" ]; then
            add_finding "HIGH" "deps" "$cargo_file" "0" \
                "Old Substrate version" \
                    "Substrate version $substrate_ver is outdated — may contain known vulnerabilities" \
                    "Update to latest stable Substrate version"
        fi

        # Check for old polkadot-sdk
        local polkadot_ver=$(grep -oP 'polkadot.*version\s*=\s*"\K[^"]+' "$cargo_file" 2>/dev/null | head -1)
        if [ -n "$polkadot_ver" ] && [ "$polkadot_ver" \< "5" ]; then
            add_finding "MEDIUM" "deps" "$cargo_file" "0" \
                "Old Polkadot SDK version" \
                    "Polkadot SDK version $polkadot_ver may have known issues" \
                    "Consider upgrading to latest stable"
        fi
    fi

    # Count total dependencies
    local dep_count=$(grep -c "^name = " "$cargo_lock" 2>/dev/null || echo "0")
    add_info "deps" "Total dependencies: $dep_count"

    # Check for duplicate dependencies (version conflicts)
    local dupes=$(grep "^name = " "$cargo_lock" | sort | uniq -d | head -10)
    if [ -n "$dupes" ]; then
        local dupe_count=$(echo "$dupes" | wc -l)
        add_finding "LOW" "deps" "$cargo_lock" "0" \
            "Duplicate dependencies ($dupe_count)" \
                "Multiple versions of the same crate — increases binary size and attack surface" \
                "Run cargo tree -d to identify and resolve version conflicts"
        fi

    # Run cargo audit if available
    if command -v cargo-audit &>/dev/null; then
        add_info "deps" "Running cargo audit..."
        cd "$PROJECT_PATH" && cargo audit 2>&1 | head -50 >> "$REPORT_FILE"
    else
        add_info "deps" "cargo-audit not installed — install with: cargo install cargo-audit"
    fi

    add_info "deps" "Dependency audit complete"
}

# ============ SCANNER: GENESIS ============
scan_genesis() {
    echo -e "${BOLD}${MAGENTA}=== Genesis Security Audit ===${NC}"
    echo "## Genesis Security Audit" >> "$REPORT_FILE"

    local chain_specs=$(find "$PROJECT_PATH" -name "*chain-spec*" -o -name "*genesis*" | grep -v target | grep -v ".git" | head -10)

    for spec in $chain_specs; do
        if [ ! -f "$spec" ]; then continue; fi

        # Check for sudo key in genesis
        if grep -q "sudo\|Sudo" "$spec" 2>/dev/null; then
            local sudo_key=$(grep -oP '"key"\s*:\s*"\K[^"]+' "$spec" 2>/dev/null | head -1)
            if [ -n "$sudo_key" ]; then
                add_finding "MEDIUM" "genesis" "$spec" "0" \
                    "Sudo key in genesis" \
                        "Sudo key is present in chain spec — central point of failure" \
                        "Remove sudo pallet before mainnet, or ensure key is in a multisig"
                fi
        fi

        # Check for hardcoded balances
        local balances=$(grep -c "balance" "$spec" 2>/dev/null || echo "0")
        if [ "$balances" -gt 0 ]; then
            add_info "genesis" "$spec: $balances balance entries in genesis"
        fi

        # Check for single validator (centralization)
        local auth_count=$(grep -c "Authority\|validator\|Validator" "$spec" 2>/dev/null || echo "0")
        if [ "$auth_count" -lt 4 ]; then
            add_finding "HIGH" "genesis" "$spec" "0" \
                "Low validator count in genesis ($auth_count)" \
                    "Chain starts with very few validators — high centralization risk" \
                    "Start with at least 7-21 validators for meaningful decentralization"
        fi
    done

    # Check for deterministic genesis
    local node_dir="$PROJECT_PATH/node"
    if [ -d "$node_dir" ]; then
        if ! find "$node_dir" -name "*.json" | xargs grep -l "session\|Session" 2>/dev/null | head -1 | grep -q .; then
            add_finding "MEDIUM" "genesis" "$node_dir" "0" \
                "Session keys may not be deterministic" \
                    "Session keys in genesis should be deterministic and well-documented" \
                    "Ensure all validator session keys are generated deterministically and documented"
        fi
    fi

    add_info "genesis" "Genesis audit complete"
}

# ============ SCANNER: RPC ============
scan_rpc() {
    echo -e "${BOLD}${MAGENTA}=== RPC Security Audit ===${NC}"
    echo "## RPC Security Audit" >> "$REPORT_FILE"

    # Check runtime RPC implementations
    local runtime_dir="$PROJECT_PATH/runtime/src"
    if [ -d "$runtime_dir" ]; then
        # Check for unsafe RPC methods
        local rpc_methods=$(grep -rn "fn .*Runtime.*for Runtime\|impl.*Api.*for Runtime" "$runtime_dir" --include="*.rs" | head -10)

        while IFS= read -r line_match; do
            [ -z "$line_match" ] && continue
            local file=$(echo "$line_match" | cut -d: -f1)
            local line_no=$(echo "$line_match" | cut -d: -f2)

            # Check if there are setter/mutation methods exposed
            local context=$(sed -n "$((line_no)),$((line_no + 50))p" "$file")
            if echo "$context" | grep -qi "fn set_\|fn update_\|fn execute_\|fn send_\|fn transfer_"; then
                add_finding "MEDIUM" "rpc" "$file" "$line_no" \
                    "Potentially unsafe RPC method" \
                        "Runtime API exposes mutation methods — if RPC is publicly accessible, these could be abused" \
                        "Ensure mutation methods are read-only queries, or require authentication"
                fi
        done <<< "$rpc_methods"
    fi

    # Check node RPC configuration
    local node_src="$PROJECT_PATH/node/src"
    if [ -d "$node_src" ]; then
        local rpc_config=$(grep -rn "rpc_methods\|RpcExtension\|rpc.*public\|rpc.*unsafe" "$node_src" --include="*.rs" | head -10)
        while IFS= read -r line_match; do
            [ -z "$line_match" ] && continue
            local file=$(echo "$line_match" | cut -d: -f1)
            local line_no=$(echo "$line_match" | cut -d: -f2)
            if echo "$line_match" | grep -qi "unsafe.*true\|UnsafeRpc.*true\|rpc.*public.*true"; then
                add_finding "HIGH" "rpc" "$file" "$line_no" \
                    "Unsafe RPC methods enabled" \
                        "Unsafe RPC methods are enabled — can execute arbitrary runtime calls" \
                        "Disable unsafe RPC methods: --rpc-methods=Safe"
                fi
        done <<< "$rpc_config"
    fi

    add_info "rpc" "RPC audit complete"
}

# ============ RUN SCANNERS ============
run_quick() {
    scan_secrets
    scan_access
    scan_infrastructure
}

run_full() {
    scan_access
    scan_arithmetic
    scan_secrets
    scan_reentrancy
    scan_economic
    scan_storage
    scan_infrastructure
    scan_deps
    scan_genesis
    scan_rpc
}

# ============ MAIN ============
echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════╗"
echo "║     Verdis Chain Security Audit Scanner     ║"
echo "║          v1.0 - Substrate/Rust              ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}Target:${NC} $PROJECT_PATH"
echo -e "${CYAN}Scan Type:${NC} $SCAN_TYPE"
echo -e "${CYAN}Time:${NC} $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}ERROR: Project path not found: $PROJECT_PATH${NC}"
    exit 1
fi

case "$SCAN_TYPE" in
    full)       run_full ;;
    quick)      run_quick ;;
    access)     scan_access ;;
    arithmetic) scan_arithmetic ;;
    secrets)    scan_secrets ;;
    reentrancy) scan_reentrancy ;;
    economic)   scan_economic ;;
    storage)    scan_storage ;;
    infrastructure) scan_infrastructure ;;
    deps)       scan_deps ;;
    genesis)    scan_genesis ;;
    rpc)        scan_rpc ;;
    *)
        echo "Usage: $0 <full|quick|access|arithmetic|secrets|reentrancy|economic|storage|infrastructure|deps|genesis|rpc> <project_path>"
        exit 1
        ;;
esac

# ============ SUMMARY ============
echo ""
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════${NC}"
echo -e "${BOLD}SECURITY AUDIT SUMMARY${NC}"
echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════${NC}"
echo -e "${BOLD}Total Findings: ${TOTAL}${NC}"
echo -e "${RED}  CRITICAL: ${CRITICAL}${NC}"
echo -e "${YELLOW}  HIGH:     ${HIGH}${NC}"
echo -e "${YELLOW}  MEDIUM:   ${MEDIUM}${NC}"
echo -e "${GREEN}  LOW:      ${LOW}${NC}"
echo ""

# Append summary to report
echo "## Summary" >> "$REPORT_FILE"
echo "- **Total Findings:** $TOTAL" >> "$REPORT_FILE"
echo "- **CRITICAL:** $CRITICAL" >> "$REPORT_FILE"
echo "- **HIGH:** $HIGH" >> "$REPORT_FILE"
echo "- **MEDIUM:** $MEDIUM" >> "$REPORT_FILE"
echo "- **LOW:** $LOW" >> "$REPORT_FILE"

if [ $CRITICAL -gt 0 ]; then
    echo -e "${RED}${BOLD}⚠  $CRITICAL CRITICAL findings — fix immediately!${NC}"
fi
if [ $HIGH -gt 0 ]; then
    echo -e "${YELLOW}${BOLD}⚠  $HIGH HIGH findings — fix before mainnet${NC}"
fi

echo ""
echo -e "${CYAN}Full report saved to: $REPORT_FILE${NC}"
