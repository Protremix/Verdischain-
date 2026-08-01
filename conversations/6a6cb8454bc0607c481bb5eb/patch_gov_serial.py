#!/usr/bin/env python3
"""Fix governance getProposal serialization (Maps can't be JSON.stringify'd)"""

with open('/opt/verdis/app/dist/core/governance.js') as f:
    content = f.read()

old = """    getProposal(id) {
        const p = this.proposals.get(id);
        if (!p) return null;
        return {
            ...p,
            voters: p.voters.size,
            voterList: Array.from(p.voters.entries()).slice(0, 20),
        };
    }"""

new = """    getProposal(id) {
        const p = this.proposals.get(id);
        if (!p) return null;
        return {
            id: p.id,
            proposer: p.proposer,
            title: p.title,
            description: p.description,
            type: p.type,
            actions: p.actions,
            status: p.status,
            forVotes: p.forVotes,
            againstVotes: p.againstVotes,
            abstainVotes: p.abstainVotes,
            voterCount: p.voters.size,
            createdAt: p.createdAt,
            votingStartsAt: p.votingStartsAt,
            votingEndsAt: p.votingEndsAt,
            timelockEndsAt: p.timelockEndsAt,
            executionEndsAt: p.executionEndsAt,
            executedAt: p.executedAt,
            canceledAt: p.canceledAt,
        };
    }"""

if old in content:
    content = content.replace(old, new)
    print("Fixed getProposal serialization")
else:
    print("ERROR: getProposal not found")

with open('/opt/verdis/app/dist/core/governance.js', 'w') as f:
    f.write(content)
print("Done!")
