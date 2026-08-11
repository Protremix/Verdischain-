# Verdis Chain Security Audit Skill

Comprehensive cybersecurity scanner for Substrate/Rust blockchain codebases.
Designed for the Verdis Chain project but works on any Substrate-based chain.

## Usage

```bash
# Full audit (all scanners)
bash .agents/skills/verdis-security-audit/scan.sh full /opt/verdis-chain-rust

# Quick scan (critical only)
bash .agents/skills/verdis-security-audit/scan.sh quick /opt/verdis-chain-rust

# Specific scanner
bash .agents/skills/verdis-security-audit/scan.sh access /opt/verdis-chain-rust
bash .agents/skills/verdis-security-audit/scan.sh arithmetic /opt/verdis-chain-rust
bash .agents/skills/verdis-security-audit/scan.sh secrets /opt/verdis-chain-rust
bash .agents/skills/verdis-security-audit/scan.sh reentrancy /opt/verdis-chain-rust
bash .agents/skills/verdis-security-audit/scan.sh economic /opt/verdis-chain-rust
bash .agents/skills/verdis-security-audit/scan.sh storage /opt/verdis-chain-rust
bash .agents/skills/verdis-security-audit/scan.sh infrastructure /opt/verdis-chain-rust
bash .agents/skills/verdis-security-audit/scan.sh deps /opt/verdis-chain-rust
```

## Scanners

1. **access** — Access control audit (ensure_root vs ensure_signed, privileged functions)
2. **arithmetic** — Overflow/underflow, unsafe casts, saturating arithmetic
3. **secrets** — Hardcoded keys, mnemonics, private keys, API tokens
4. **reentrancy** — Reentrancy patterns, callback vulnerabilities
5. **economic** — Economic attack vectors, slashing math, staking rewards
6. **storage** — Storage corruption, unbounded growth, missing bounds
7. **infrastructure** — Network security, port exposure, Docker, nginx
8. **deps** — Dependency audit, outdated crates, known CVEs
9. **genesis** — Genesis config security, key distribution, initial balances
10. **rpc** — RPC endpoint security, exposed methods, auth bypass

## Output

Findings classified as:
- **CRITICAL** — Exploitable, funds at risk
- **HIGH** — Security bypass or privilege escalation
- **MEDIUM** — Best practice violation with risk
- **LOW** — Informational, hardening recommendation

Generates a structured report with file, line, finding, and remediation.
