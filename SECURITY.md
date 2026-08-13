# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Verdis Chain, please report it responsibly:

1. **Do NOT open a public GitHub issue**
2. Email: contact via [verdischain.com/contact](https://verdischain.com/contact/)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a timeline for a fix.

## Security Measures

- No hardcoded private keys, mnemonics, or backdoors
- User transaction signing on user's wallet/device only
- TX Relay uses AES-GCM encryption
- All extrinsic parameters bounded with length checks
- Safe integer casts (no unsafe `as` conversions)
- Docker containers run as non-root with read-only FS
- SSH key-only authentication on servers
- UFW firewall configured
- Nginx HSTS, CSP, X-XSS-Protection headers

## Supported Versions

| Version | Supported |
|---|---|
| 2.0.x | ✅ |
| < 2.0 | ❌ |
