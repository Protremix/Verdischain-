"use strict";
/**
 * Verdis On-Chain Governance
 * 
 * Decentralized protocol governance with:
 * - Proposal creation (parameter changes, treasury spending, upgrades)
 * - On-chain voting (1 VRS staked = 1 vote)
 * - Quorum and threshold requirements
 * - Execution of approved proposals
 * - Timelock for safety
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.Governance = void 0;
class Governance {
    constructor(tokenSystem) {
        this.tokenSystem = tokenSystem;
        this.proposals = new Map();
        this.nextProposalId = 1;
        this.votingPeriodMs = 72 * 60 * 60 * 1000;     // 72 hours
        this.timelockMs = 24 * 60 * 60 * 1000;         // 24h timelock after approval
        this.executionPeriodMs = 7 * 24 * 60 * 60 * 1000; // 7 days to execute
        this.quorumVotesPct = 0.10;                     // 10% of total supply must vote
        this.thresholdPct = 0.66;                       // 66% yes votes to pass
        this.minProposalStake = 100000;                // 100K VRS to create proposal
    }
    /**
     * Create a new governance proposal
     */
    createProposal(proposer, title, description, proposalType, actions, stakeAmount) {
        // Verify proposer has enough stake
        const staked = this.tokenSystem.getStaked(proposer);
        if (staked < this.minProposalStake) {
            return { success: false, error: `Need at least ${this.minProposalStake} VRS staked to propose` };
        }
        const id = this.nextProposalId++;
        const now = Date.now();
        const proposal = {
            id,
            proposer,
            title,
            description,
            type: proposalType,     // 'parameter_change', 'treasury_spend', 'upgrade', 'other'
            actions: actions || [],
            status: 'active',       // 'active', 'passed', 'failed', 'executed', 'canceled', 'timelocked'
            forVotes: 0,
            againstVotes: 0,
            abstainVotes: 0,
            voters: new Map(),      // address -> {vote, weight, timestamp}
            createdAt: now,
            votingStartsAt: now,
            votingEndsAt: now + this.votingPeriodMs,
            timelockEndsAt: 0,      // Set when passed
            executionEndsAt: 0,     // Set when timelocked
            executedAt: 0,
            canceledAt: 0,
        };
        this.proposals.set(id, proposal);
        return { success: true, proposalId: id };
    }
    /**
     * Cast a vote on a proposal
     */
    castVote(voter, proposalId, vote) {
        const proposal = this.proposals.get(proposalId);
        if (!proposal) return { success: false, error: "Proposal not found" };
        if (proposal.status !== 'active') return { success: false, error: "Proposal not active" };
        const now = Date.now();
        if (now < proposal.votingStartsAt) return { success: false, error: "Voting not started" };
        if (now > proposal.votingEndsAt) return { success: false, error: "Voting ended" };
        if (proposal.voters.has(voter)) return { success: false, error: "Already voted" };
        if (vote !== 'for' && vote !== 'against' && vote !== 'abstain') {
            return { success: false, error: "Invalid vote: must be 'for', 'against', or 'abstain'" };
        }
        // Voting power = staked VRS
        const votingPower = this.tokenSystem.getStaked(voter);
        if (votingPower === 0) return { success: false, error: "No voting power (no VRS staked)" };
        proposal.voters.set(voter, { vote, weight: votingPower, timestamp: now });
        if (vote === 'for') proposal.forVotes += votingPower;
        else if (vote === 'against') proposal.againstVotes += votingPower;
        else proposal.abstainVotes += votingPower;
        this.proposals.set(proposalId, proposal);
        return {
            success: true,
            vote,
            votingPower,
            totalFor: proposal.forVotes,
            totalAgainst: proposal.againstVotes,
        };
    }
    /**
     * Tally votes and update proposal status
     */
    tallyVotes(proposalId) {
        const proposal = this.proposals.get(proposalId);
        if (!proposal) return { success: false, error: "Proposal not found" };
        if (proposal.status !== 'active') return { success: false, error: `Proposal already ${proposal.status}` };
        if (Date.now() < proposal.votingEndsAt) return { success: false, error: "Voting still in progress" };
        const totalVotes = proposal.forVotes + proposal.againstVotes + proposal.abstainVotes;
        const totalSupply = this.tokenSystem.getTotalSupply();
        const quorum = Math.floor(totalSupply * this.quorumVotesPct);
        // Check quorum
        if (totalVotes < quorum) {
            proposal.status = 'failed';
            proposal.canceledAt = Date.now();
            this.proposals.set(proposalId, proposal);
            return { success: true, result: 'failed', reason: `Quorum not met: ${totalVotes}/${quorum}` };
        }
        // Check threshold (yes votes / (yes + no), excluding abstain)
        const decisiveVotes = proposal.forVotes + proposal.againstVotes;
        if (decisiveVotes === 0) {
            proposal.status = 'failed';
            this.proposals.set(proposalId, proposal);
            return { success: true, result: 'failed', reason: "No decisive votes" };
        }
        const yesPct = proposal.forVotes / decisiveVotes;
        if (yesPct >= this.thresholdPct) {
            proposal.status = 'timelocked';
            proposal.timelockEndsAt = Date.now() + this.timelockMs;
            proposal.executionEndsAt = proposal.timelockEndsAt + this.executionPeriodMs;
            this.proposals.set(proposalId, proposal);
            return {
                success: true,
                result: 'passed',
                forVotes: proposal.forVotes,
                againstVotes: proposal.againstVotes,
                yesPct: yesPct * 100,
                timelockEndsAt: proposal.timelockEndsAt,
            };
        } else {
            proposal.status = 'failed';
            proposal.canceledAt = Date.now();
            this.proposals.set(proposalId, proposal);
            return {
                success: true,
                result: 'failed',
                forVotes: proposal.forVotes,
                againstVotes: proposal.againstVotes,
                yesPct: yesPct * 100,
                reason: `Threshold not met: ${(yesPct * 100).toFixed(1)}% < ${(this.thresholdPct * 100).toFixed(1)}%`,
            };
        }
    }
    /**
     * Execute a passed proposal (after timelock)
     */
    executeProposal(proposalId, callerAddress) {
        const proposal = this.proposals.get(proposalId);
        if (!proposal) return { success: false, error: "Proposal not found" };
        if (proposal.status !== 'timelocked') return { success: false, error: `Proposal status: ${proposal.status}` };
        if (Date.now() < proposal.timelockEndsAt) return { success: false, error: "Timelock not expired" };
        if (Date.now() > proposal.executionEndsAt) {
            proposal.status = 'failed';
            proposal.canceledAt = Date.now();
            this.proposals.set(proposalId, proposal);
            return { success: false, error: "Execution window expired" };
        }
        // Execute actions
        const results = [];
        for (const action of proposal.actions) {
            results.push(this.executeAction(action, callerAddress));
        }
        proposal.status = 'executed';
        proposal.executedAt = Date.now();
        this.proposals.set(proposalId, proposal);
        return { success: true, results };
    }
    executeAction(action, callerAddress) {
        switch (action.type) {
            case 'treasury_spend': {
                const amount = this.tokenSystem.getBalance(this.tokenSystem.treasuryAddress);
                if (amount < action.amount) {
                    return { type: 'treasury_spend', success: false, error: "Insufficient treasury balance" };
                }
                // Transfer from treasury to recipient
                this.tokenSystem.deductBalance(this.tokenSystem.treasuryAddress, action.amount);
                this.tokenSystem.addBalance(action.recipient, action.amount);
                return { type: 'treasury_spend', success: true, amount: action.amount, recipient: action.recipient };
            }
            case 'parameter_change': {
                // Record the parameter change (actual execution would modify protocol params)
                return { type: 'parameter_change', success: true, parameter: action.parameter, newValue: action.newValue };
            }
            case 'upgrade': {
                return { type: 'upgrade', success: true, description: action.description };
            }
            default:
                return { type: action.type, success: false, error: "Unknown action type" };
        }
    }
    /**
     * Cancel a proposal (only proposer)
     */
    cancelProposal(proposalId, callerAddress) {
        const proposal = this.proposals.get(proposalId);
        if (!proposal) return { success: false, error: "Proposal not found" };
        if (proposal.status === 'executed') return { success: false, error: "Already executed" };
        if (proposal.proposer !== callerAddress) return { success: false, error: "Only proposer can cancel" };
        proposal.status = 'canceled';
        proposal.canceledAt = Date.now();
        this.proposals.set(proposalId, proposal);
        return { success: true };
    }
    getProposal(id) {
        const p = this.proposals.get(id);
        if (!p) return null;
        return {
            ...p,
            voters: p.voters.size,
            voterList: Array.from(p.voters.entries()).slice(0, 20),
        };
    }
    getAllProposals() {
        return Array.from(this.proposals.values()).map(p => ({
            id: p.id,
            proposer: p.proposer,
            title: p.title,
            description: p.description,
            type: p.type,
            status: p.status,
            forVotes: p.forVotes,
            againstVotes: p.againstVotes,
            abstainVotes: p.abstainVotes,
            voterCount: p.voters.size,
            createdAt: p.createdAt,
            votingEndsAt: p.votingEndsAt,
            timelockEndsAt: p.timelockEndsAt,
            executionEndsAt: p.executionEndsAt,
            executedAt: p.executedAt,
        }));
    }
    getActiveProposals() {
        return this.getAllProposals().filter(p => p.status === 'active');
    }
    getStats() {
        const all = Array.from(this.proposals.values());
        return {
            totalProposals: all.length,
            active: all.filter(p => p.status === 'active').length,
            passed: all.filter(p => p.status === 'timelocked' || p.status === 'executed').length,
            failed: all.filter(p => p.status === 'failed').length,
            executed: all.filter(p => p.status === 'executed').length,
            canceled: all.filter(p => p.status === 'canceled').length,
            totalVotes: all.reduce((s, p) => s + p.forVotes + p.againstVotes + p.abstainVotes, 0),
            votingPeriodHours: this.votingPeriodMs / (60 * 60 * 1000),
            timelockHours: this.timelockMs / (60 * 60 * 1000),
            quorumPct: this.quorumVotesPct * 100,
            thresholdPct: this.thresholdPct * 100,
        };
    }
    exportState() {
        return {
            proposals: Array.from(this.proposals.entries()).map(([id, p]) => [
                id,
                { ...p, voters: Array.from(p.voters.entries()) }
            ]),
            nextProposalId: this.nextProposalId,
        };
    }
    importState(state) {
        if (state.proposals) {
            for (const [id, p] of state.proposals) {
                p.voters = new Map(p.voters);
                this.proposals.set(id, p);
            }
        }
        if (state.nextProposalId) this.nextProposalId = state.nextProposalId;
    }
}
exports.Governance = Governance;
