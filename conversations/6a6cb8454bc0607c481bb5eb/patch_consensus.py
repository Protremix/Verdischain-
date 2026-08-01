#!/usr/bin/env python3
"""Patch consensus.js: Add fee burn mechanism + gas abstraction support"""

with open('/opt/verdis/app/dist/core/consensus.js') as f:
    content = f.read()

# Fix 1: Add fee burn rate and burn tracking to TokenSystem
old_class = """class TokenSystem {
    constructor() {
        this.balances = new Map();
        this.stakes = new Map();
        this.maxSupply = 100000000000; // 100 billion
        this.totalSupply = 0;
        this.blockReward = 16; // VRS per block (like Tron)
    }"""

new_class = """class TokenSystem {
    constructor() {
        this.balances = new Map();
        this.stakes = new Map();
        this.maxSupply = 100000000000; // 100 billion
        this.totalSupply = 0;
        this.blockReward = 16; // VRS per block (like Tron)
        this.feeBurnRate = 0.5; // 50% of fees burned (deflationary)
        this.totalFeesBurned = 0; // Track total burned fees
        this.totalFeesDistributed = 0; // Track total distributed fees
        this.treasuryAddress = '0x0000000000000000000000000000000000007472'; // Treasury
        this.treasuryRate = 0.1; // 10% of block reward to treasury
        this.gasAbstractionEnabled = true; // Allow dApps to sponsor gas
        this.gasSponsorships = new Map(); // contract -> sponsor balance
    }"""

if old_class in content:
    content = content.replace(old_class, new_class)
    print("1. Added fee burn + treasury + gas abstraction to TokenSystem")
else:
    print("1. ERROR: TokenSystem constructor not found")

# Fix 2: Update applyTransaction to burn fees
old_apply = """applyTransaction(tx, blockProducer) {
        // Deduct amount + fee from sender
        if (!this.deductBalance(tx.from, tx.amount + tx.fee))
            return false;
        // Add amount to receiver
        this.addBalance(tx.to, tx.amount);
        // Fee goes to block producer
        if (tx.fee > 0) {
            this.addBalance(blockProducer, tx.fee);
        }
        return true;
    }"""

new_apply = """applyTransaction(tx, blockProducer) {
        // Check if gas is sponsored (gas abstraction)
        const sponsor = tx.gasSponsor;
        if (sponsor && this.gasAbstractionEnabled && this.gasSponsorships.has(sponsor)) {
            const sponsorBalance = this.gasSponsorships.get(sponsor);
            if (sponsorBalance >= tx.fee) {
                // Sponsor pays the gas, not the sender
                if (!this.deductBalance(tx.from, tx.amount))
                    return false;
                this.addBalance(tx.to, tx.amount);
                // Deduct from sponsor pool
                this.gasSponsorships.set(sponsor, sponsorBalance - tx.fee);
                // Apply fee burn to sponsored gas
                const burnAmount = Math.floor(tx.fee * this.feeBurnRate);
                this.totalFeesBurned += burnAmount;
                const producerAmount = tx.fee - burnAmount;
                this.totalFeesDistributed += producerAmount;
                this.addBalance(blockProducer, producerAmount);
                return true;
            }
        }
        // Standard: deduct amount + fee from sender
        if (!this.deductBalance(tx.from, tx.amount + tx.fee))
            return false;
        // Add amount to receiver
        this.addBalance(tx.to, tx.amount);
        // Fee: burn portion + producer portion
        if (tx.fee > 0) {
            const burnAmount = Math.floor(tx.fee * this.feeBurnRate);
            this.totalFeesBurned += burnAmount;
            const producerAmount = tx.fee - burnAmount;
            this.totalFeesDistributed += producerAmount;
            this.addBalance(blockProducer, producerAmount);
            // Burned amount is simply not re-issued (reduces circulating supply)
        }
        return true;
    }"""

if old_apply in content:
    content = content.replace(old_apply, new_apply)
    print("2. Updated applyTransaction with fee burn + gas sponsorship")
else:
    print("2. ERROR: applyTransaction not found")

# Fix 3: Add gas sponsorship methods + treasury allocation in distributeRewards
old_distribute = """distributeRewards(producer, tokenSystem) {
        const reward = tokenSystem.getBlockReward();
        // 80% to producer
        const producerReward = Math.floor(reward * 0.8);
        tokenSystem.addBalance(producer.address, producerReward);
        producer.totalRewards += producerReward;
        // 20% to voters proportional to stake
        const voterStakes = this.stakes.filter(s => s.validator === producer.address);
        const totalVoterStake = voterStakes.reduce((sum, s) => sum + s.amount, 0);
        if (totalVoterStake > 0) {
            const voterRewardPool = reward - producerReward;
            for (const stakeEntry of voterStakes) {
                const share = Math.floor(voterRewardPool * (stakeEntry.amount / totalVoterStake));
                if (share > 0) {
                    tokenSystem.addBalance(stakeEntry.voter, share);
                }
            }
        }
    }"""

new_distribute = """distributeRewards(producer, tokenSystem) {
        const reward = tokenSystem.getBlockReward();
        // 70% to producer
        const producerReward = Math.floor(reward * 0.70);
        tokenSystem.addBalance(producer.address, producerReward);
        producer.totalRewards += producerReward;
        // 20% to voters proportional to stake
        const voterStakes = this.stakes.filter(s => s.validator === producer.address);
        const totalVoterStake = voterStakes.reduce((sum, s) => sum + s.amount, 0);
        const voterRewardPool = Math.floor(reward * 0.20);
        if (totalVoterStake > 0) {
            for (const stakeEntry of voterStakes) {
                const share = Math.floor(voterRewardPool * (stakeEntry.amount / totalVoterStake));
                if (share > 0) {
                    tokenSystem.addBalance(stakeEntry.voter, share);
                }
            }
        }
        // 10% to treasury for ecosystem development
        const treasuryAmount = reward - producerReward - voterRewardPool;
        if (treasuryAmount > 0 && tokenSystem.treasuryAddress) {
            tokenSystem.addBalance(tokenSystem.treasuryAddress, treasuryAmount);
        }
    }"""

if old_distribute in content:
    content = content.replace(old_distribute, new_distribute)
    print("3. Updated reward distribution: 70% producer, 20% voters, 10% treasury")
else:
    print("3. ERROR: distributeRewards not found")

# Add gas sponsorship methods after getBlockReward
old_methods = """getBlockReward() {
        return this.blockReward;
    }"""

new_methods = """getBlockReward() {
        return this.blockReward;
    }
    depositGasSponsorship(sponsor, amount) {
        if (!this.deductBalance(sponsor, amount))
            return false;
        const current = this.gasSponsorships.get(sponsor) || 0;
        this.gasSponsorships.set(sponsor, current + amount);
        return true;
    }
    getGasSponsorshipBalance(sponsor) {
        return this.gasSponsorships.get(sponsor) || 0;
    }
    withdrawGasSponsorship(sponsor, amount) {
        const current = this.gasSponsorships.get(sponsor) || 0;
        if (current < amount)
            return false;
        this.gasSponsorships.set(sponsor, current - amount);
        this.addBalance(sponsor, amount);
        return true;
    }
    getFeesBurned() {
        return this.totalFeesBurned;
    }
    getFeesDistributed() {
        return this.totalFeesDistributed;
    }
    getTreasuryBalance() {
        return this.getBalance(this.treasuryAddress);
    }"""

if old_methods in content:
    content = content.replace(old_methods, new_methods)
    print("4. Added gas sponsorship + treasury + fee burn methods")
else:
    print("4. ERROR: getBlockReward not found")

with open('/opt/verdis/app/dist/core/consensus.js', 'w') as f:
    f.write(content)
print("Consensus.js patched successfully!")
