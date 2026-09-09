#!/usr/bin/env python3
"""Sale Eligibility Engine for Verdis Chain VRDX token sale.
Sale is currently DISABLED. This is infrastructure preparation only."""
import json, os, csv, ipaddress, sys
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional

# Jurisdiction statuses
class JurisdictionStatus(Enum):
    ALLOW = 'ALLOW'
    RESTRICT = 'RESTRICT'
    BLOCK = 'BLOCK'
    LEGAL_REVIEW_REQUIRED = 'LEGAL_REVIEW_REQUIRED'

# KYC status
class KYCStatus(Enum):
    NOT_STARTED = 'NOT_STARTED'
    PENDING = 'PENDING'
    VERIFIED = 'VERIFIED'
    REJECTED = 'REJECTED'

# Sanctions status
class SanctionsStatus(Enum):
    CLEAR = 'CLEAR'
    FLAGGED = 'FLAGGED'
    ERROR = 'ERROR'

@dataclass
class EligibilityResult:
    eligible: bool = False
    reasons: List[str] = field(default_factory=list)
    tier: str = 'BLOCKED'

class SaleEligibilityEngine:
    def __init__(self, config_path='sale_config.json'):
        self.config = self._load_config(config_path)
        self.jurisdictions = self._load_jurisdictions()

    def _load_config(self, path):
        default = {
            'sale_enabled': False,
            'min_age': 18,
            'allowed_jurisdictions': [],
            'restricted_jurisdictions': [],
            'blocked_jurisdictions': []
        }
        if os.path.exists(path):
            with open(path) as f:
                default.update(json.load(f))
        return default

    def _load_jurisdictions(self):
        jurisdictions = {}
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'legal', 'global', 'JURISDICTION_MATRIX.csv')
        if os.path.exists(csv_path):
            with open(csv_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    country = row.get('Country', '').strip()
                    status = row.get('Token_Classification', 'LEGAL_REVIEW_REQUIRED').strip()
                    jurisdictions[country] = status
        return jurisdictions

    def check_sale_enabled(self):
        if not self.config.get('sale_enabled', False):
            return False, 'Sale is not active'
        return True, ''

    def check_jurisdiction(self, country_code):
        status = self.jurisdictions.get(country_code, 'LEGAL_REVIEW_REQUIRED')
        if status in ('BLOCK', 'LEGAL_REVIEW_REQUIRED'):
            return False, f'Jurisdiction {country_code} is {status}'
        if status == 'RESTRICT':
            return False, f'Jurisdiction {country_code} requires manual review'
        if status == 'ALLOW':
            return True, ''
        return False, f'Jurisdiction {country_code} status unknown'

    def check_kyc_status(self, user_id):
        """Stub — real KYC provider not yet selected."""
        return KYCStatus.NOT_STARTED

    def check_sanctions(self, name, wallet_address):
        """Stub — real screening provider not yet selected."""
        return SanctionsStatus.ERROR

    def check_age(self, date_of_birth):
        """Stub — real age verification via KYC provider."""
        return False  # Cannot verify without KYC provider

    def check_eligibility(self, user):
        result = EligibilityResult()

        # 1. Sale must be enabled
        sale_ok, reason = self.check_sale_enabled()
        if not sale_ok:
            result.reasons.append(reason)
            return result

        # 2. Jurisdiction check
        country = user.get('country', '')
        jur_ok, reason = self.check_jurisdiction(country)
        if not jur_ok:
            result.reasons.append(reason)
            return result

        # 3. KYC check
        kyc = self.check_kyc_status(user.get('id'))
        if kyc != KYCStatus.VERIFIED:
            result.reasons.append(f'KYC status: {kyc.value}')
            return result

        # 4. Sanctions check
        sanctions = self.check_sanctions(user.get('name'), user.get('wallet'))
        if sanctions != SanctionsStatus.CLEAR:
            result.reasons.append(f'Sanctions status: {sanctions.value}')
            return result

        # 5. Age check
        if not self.check_age(user.get('date_of_birth')):
            result.reasons.append('Age not verified')
            return result

        result.eligible = True
        result.tier = 'TIER_1'
        return result

# Unit tests
def run_tests():
    print('=== Sale Eligibility Engine Tests ===')
    engine = SaleEligibilityEngine()
    passed = 0
    failed = 0

    # Test 1: Sale disabled
    r = engine.check_eligibility({'id': 'u1', 'country': 'EU/EEA'})
    assert not r.eligible, 'Should be blocked when sale disabled'
    assert 'Sale is not active' in r.reasons[0]
    print('[PASS] Sale disabled blocks all users')
    passed += 1

    # Test 2: Jurisdiction check - blocked country
    ok, reason = engine.check_jurisdiction('USA')
    assert not ok, 'USA should be blocked (LEGAL_REVIEW_REQUIRED)'
    print('[PASS] Unknown/blocked jurisdiction rejected')
    passed += 1

    # Test 3: Jurisdiction check - unknown
    ok, reason = engine.check_jurisdiction('UNKNOWN_COUNTRY')
    assert not ok, 'Unknown country should be blocked'
    print('[PASS] Unknown country rejected')
    passed += 1

    # Test 4: KYC stub returns NOT_STARTED
    kyc = engine.check_kyc_status('any_user')
    assert kyc == KYCStatus.NOT_STARTED
    print('[PASS] KYC stub returns NOT_STARTED')
    passed += 1

    # Test 5: Sanctions stub returns ERROR
    s = engine.check_sanctions('test', '0x123')
    assert s == SanctionsStatus.ERROR
    print('[PASS] Sanctions stub returns ERROR')
    passed += 1

    # Test 6: Sale enabled but no KYC
    engine.config['sale_enabled'] = True
    r = engine.check_eligibility({'id': 'u1', 'country': 'ALLOW_COUNTRY'})
    assert not r.eligible, 'Should fail without KYC'
    print('[PASS] Sale enabled but KYC blocks')
    passed += 1

    print(f'\n=== Results: {passed} passed, {failed} failed ===')

if __name__ == '__main__':
    run_tests()
