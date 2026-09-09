# Verdis Chain Bug Bounty & Responsible Disclosure (ARCH-054)

**Status:** Draft — formalize before mainnet

---

## 1. Responsible Disclosure Policy

Verdis Chain welcomes responsible disclosure of security vulnerabilities. We are committed to working with security researchers to verify and address vulnerabilities promptly.

## 2. Scope

**In Scope:**
- Verdis Chain runtime and pallets (Rust source code)
- Verdis Chain node implementation
- Verdis Chain web wallet (client-side)
- Verdis Chain TX Relay service
- Verdis Chain infrastructure (nginx, API endpoints)
- Verdis Chain DEX (pallet-amm-dex)

**Out of Scope:**
- Third-party services not controlled by Verdis Chain
- Social engineering attacks
- DDoS attacks
- Vulnerabilities in dependencies already disclosed publicly

## 3. Reporting Process

1. Email security@verdischain.com with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested remediation (if available)

2. We acknowledge receipt within 48 hours
3. We provide an initial assessment within 7 days
4. We work with the reporter to validate and fix the issue
5. We publish a security advisory after the fix is deployed

## 4. Bounty Rewards (Proposed)

| Severity | Description | Reward (VRDX) |
|----------|-------------|---------------|
| Critical | Fund loss, consensus halt, key compromise | 500,000 |
| High | Logic exploit, DEX vulnerability | 100,000 |
| Medium | DoS, information disclosure | 25,000 |
| Low | Minor logic error, config issue | 5,000 |

Note: Rewards are proposed and subject to funding availability. Bug bounty program must be formally approved before mainnet launch.

## 5. Guidelines

- Do not exploit the vulnerability beyond what is needed to demonstrate it
- Do not access or modify other users data
- Do not publicly disclose the vulnerability before it is fixed
- Provide reasonable time for remediation (minimum 90 days)

## 6. Safe Harbor

We will not pursue legal action against researchers who:
- Follow this responsible disclosure policy
- Act in good faith
- Do not cause harm to users or the network
