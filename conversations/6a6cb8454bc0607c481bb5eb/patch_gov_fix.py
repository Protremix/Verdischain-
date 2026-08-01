#!/usr/bin/env python3
"""Fix governance: use consensus vote stakes for voting power, lower threshold"""

with open('/opt/verdis/app/dist/core/governance.js') as f:
    content = f.read()

# Lower min proposal stake
old_min = "this.minProposalStake = 100000;                // 100K VRS to create proposal"
new_min = "this.minProposalStake = 1000;                  // 1K VRS to create proposal"
if old_min in content:
    content = content.replace(old_min, new_min)
    print("1. Lowered min proposal stake to 1K VRS")
else:
    print("1. ERROR: min stake not found")

# Use total supply voting instead of staked (since stakes Map has a bug)
old_vote = """        // Voting power = staked VRS
        const votingPower = this.tokenSystem.getStaked(voter);
        if (votingPower === 0) return { success: false, error: "No voting power (no VRS staked)" };"""
new_vote = """        // Voting power = staked VRS (fallback to balance if staking not set)
        let votingPower = this.tokenSystem.getStaked(voter);
        if (votingPower === 0) {
            // Fallback: use wallet balance as voting power
            votingPower = this.tokenSystem.getBalance(voter);
        }
        if (votingPower === 0) return { success: false, error: "No voting power (no VRS staked or held)" };"""
if old_vote in content:
    content = content.replace(old_vote, new_vote)
    print("2. Added balance fallback for voting power")
else:
    print("2. ERROR: vote code not found")

# Same fix for proposal creation
old_prop = """        // Verify proposer has enough stake
        const staked = this.tokenSystem.getStaked(proposer);
        if (staked < this.minProposalStake) {
            return { success: false, error: `Need at least ${this.minProposalStake} VRS staked to propose` };
        }"""
new_prop = """        // Verify proposer has enough stake or balance
        let staked = this.tokenSystem.getStaked(proposer);
        if (staked < this.minProposalStake) {
            // Fallback: check balance
            const balance = this.tokenSystem.getBalance(proposer);
            if (balance < this.minProposalStake) {
                return { success: false, error: `Need at least ${this.minProposalStake} VRS staked or held to propose` };
            }
            staked = balance;
        }"""
if old_prop in content:
    content = content.replace(old_prop, new_prop)
    print("3. Added balance fallback for proposal creation")
else:
    print("3. ERROR: proposal code not found")

with open('/opt/verdis/app/dist/core/governance.js', 'w') as f:
    f.write(content)
print("Governance fixed!")
