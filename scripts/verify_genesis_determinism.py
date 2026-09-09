#!/usr/bin/env python3
"""Genesis Determinism Verification for Verdis Chain."""
import json, subprocess, sys, os, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BINARY = os.path.join(REPO, 'target', 'release', 'verdis-node')
SPEC_FILE = '/tmp/spec_verify.json'

checks = []

def check(name, passed, details=''):
    checks.append({'name': name, 'passed': passed, 'details': details})
    status = 'PASS' if passed else 'FAIL'
    print(f'[{status}] {name}' + (f' — {details}' if details else ''))

def build_node():
    print('Building release binary...')
    r = subprocess.run(['cargo', 'build', '--release', '--bin', 'verdis-node'],
                       capture_output=True, text=True, cwd=REPO)
    return r.returncode == 0

def generate_spec():
    r = subprocess.run([BINARY, 'build-spec', '--chain', 'testnet'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    with open(SPEC_FILE, 'w') as f:
        f.write(r.stdout)
    return r.stdout

def verify_allocations(spec):
    """Check token allocations sum to 100B * 10^9."""
    try:
        genesis = spec.get('genesis', {})
        runtime = genesis.get('runtimeGenesis', {})
        balances = runtime.get('balances', {}).get('balances', [])
        total = 0
        for addr, amount in balances:
            total += amount
        expected = 100_000_000_000 * 10**9
        check('Token allocations sum to 100B VRDX',
              total == expected,
              f'Total: {total}, Expected: {expected}')
    except Exception as e:
        check('Token allocations sum to 100B VRDX', False, str(e))

def verify_validators(spec):
    """Check 21 validators in genesis."""
    try:
        runtime = spec.get('genesis', {}).get('runtimeGenesis', {})
        dpos = runtime.get('dpos', {})
        validators = dpos.get('validators', [])
        count = len(validators)
        check('21 validators in genesis', count == 21, f'Found: {count}')
        # Check SS58 format (basic check)
        for v in validators:
            addr = v[0] if isinstance(v, list) else v.get('address', '')
            if not addr or len(addr) < 10:
                check(f'Valid address format for {addr}', False)
                break
        else:
            check('All validator addresses present', True)
    except Exception as e:
        check('21 validators in genesis', False, str(e))

def verify_no_sudo(spec):
    """Check pallet_sudo is not present."""
    runtime = spec.get('genesis', {}).get('runtimeGenesis', {})
    has_sudo = 'sudo' in runtime
    check('pallet_sudo removed', not has_sudo)

def verify_active_validator_count(spec):
    """Check ActiveValidatorCount = 21."""
    try:
        dpos = spec.get('genesis', {}).get('runtimeGenesis', {}).get('dpos', {})
        avc = dpos.get('activeValidatorCount', 0)
        check('ActiveValidatorCount = 21', avc == 21, f'Found: {avc}')
    except Exception as e:
        check('ActiveValidatorCount = 21', False, str(e))

def verify_treasury(spec):
    """Check treasury PalletId or multisig."""
    try:
        runtime = spec.get('genesis', {}).get('runtimeGenesis', {})
        has_treasury = 'treasury' in runtime
        check('Treasury pallet present', has_treasury)
        # Check team multisig placeholder
        balances = runtime.get('balances', {}).get('balances', [])
        check('Genesis has balance allocations', len(balances) > 0,
              f'{len(balances)} entries')
    except Exception as e:
        check('Treasury pallet present', False, str(e))

def verify_determinism():
    """Build spec twice and compare."""
    print('Generating spec #1...')
    spec1 = generate_spec()
    print('Generating spec #2...')
    spec2 = generate_spec()
    if spec1 is None or spec2 is None:
        check('Spec generation deterministic', False, 'Could not generate spec')
        return
    # Compare (ignoring bootnodes/random fields)
    try:
        j1 = json.loads(spec1)
        j2 = json.loads(spec2)
        # Remove bootNodes which may differ
        j1.pop('bootNodes', None)
        j2.pop('bootNodes', None)
        h1 = hashlib.sha256(json.dumps(j1, sort_keys=True).encode()).hexdigest()
        h2 = hashlib.sha256(json.dumps(j2, sort_keys=True).encode()).hexdigest()
        check('Spec is deterministic (excluding bootNodes)', h1 == h2,
              f'Hash1: {h1[:16]}... Hash2: {h2[:16]}...')
    except Exception as e:
        check('Spec is deterministic', False, str(e))

def main():
    print('=== Verdis Chain Genesis Determinism Verification ===')
    print()

    if not os.path.exists(BINARY):
        if not build_node():
            print('ERROR: Could not build binary')
            sys.exit(1)
    else:
        print('Binary exists, skipping build')

    # Generate spec
    spec_text = generate_spec()
    if spec_text is None:
        print('ERROR: Could not generate chain spec')
        sys.exit(1)

    try:
        spec = json.loads(spec_text)
    except json.JSONDecodeError as e:
        print(f'ERROR: Spec is not valid JSON: {e}')
        sys.exit(1)

    check('Spec is valid JSON', True)

    # Run all checks
    verify_allocations(spec)
    verify_validators(spec)
    verify_no_sudo(spec)
    verify_active_validator_count(spec)
    verify_treasury(spec)
    verify_determinism()

    # Summary
    passed = sum(1 for c in checks if c['passed'])
    total = len(checks)
    print()
    print(f'=== Results: {passed}/{total} checks passed ===')
    if passed < total:
        print('FAILURES:')
        for c in checks:
            if not c['passed']:
                print(f'  - {c["name"]}: {c["details"]}')
        sys.exit(1)
    else:
        print('ALL CHECKS PASSED')

if __name__ == '__main__':
    main()
