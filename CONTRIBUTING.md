# Contributing to Verdis Chain

Thank you for your interest in contributing to Verdis Chain! This document outlines the process and standards for contributing to the project.

## Development Setup

### Prerequisites

- Rust (stable, latest stable toolchain)
- Cargo
- Git

### Build

```bash
git clone https://github.com/Protremix/Verdischain-.git
cd Verdischain-
cargo build --release
```

### Run Tests

```bash
cargo test
```

### Code Quality

Before submitting a PR, ensure all checks pass:

```bash
cargo fmt --check
cargo clippy -- -D warnings
cargo test
cargo build --release
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Ensure all tests pass (`cargo test`)
5. Ensure code is formatted (`cargo fmt`)
6. Ensure no clippy warnings (`cargo clippy`)
7. Commit with a clear message
8. Open a Pull Request using the PR template

## Code Standards

### Rust

- Follow `cargo fmt` formatting
- No `unwrap()` or `expect()` in pallet code — use proper error handling
- All extrinsic parameters must be bounded with length checks
- Use safe integer casts (`try_from`) — no unsafe `as` conversions
- Document all public functions with `///` doc comments
- Add tests for all new functionality

### Pallet Development

- Every new extrinsic needs:
  - Input validation (bounded lengths)
  - Event emission
  - Tests (success and failure cases)
- Storage items must have proper `MaxLen` bounds
- Weights must be configured

### Web Development

- All pages must use the gradient-ui-ux template
- Use CSS variables from `verdis.css` — no hardcoded colors
- Responsive: must work at 375px (mobile) and above
- WCAG 2.1 AA accessibility compliance
- No fake/hardcoded data — all data from live RPC

## Security

- **Never** commit private keys, mnemonics, or secrets
- **Never** introduce hardcoded backdoors or privileged controls
- **Never** store user private keys server-side
- User transaction signing should happen on the user's wallet/device
- Report security issues privately — do not open a public issue

## Branch Naming

- `feature/` — New features
- `fix/` — Bug fixes
- `security/` — Security fixes
- `docs/` — Documentation changes
- `refactor/` — Code refactoring

## Commit Messages

Use clear, descriptive commit messages:

```
Add validator slashing mechanism to DPoS pallet

- Implement slash_ratio storage item
- Add slash extrinsic with root origin
- Add tests for slashing scenarios
- Update weights for new extrinsic
```

## Questions

If you have questions, please:
1. Check the [documentation](docs/)
2. Open a discussion on GitHub
3. Contact us at [verdischain.com/contact](https://verdischain.com/contact/)
