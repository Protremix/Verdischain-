import sys

with open('/opt/verdis/app/dist/api/server.js', 'r') as f:
    content = f.read()

import_str = 'const token_standards_1 = require("../core/token-standards");\n'
if import_str not in content:
    content = content.replace('const security_1 = require("../core/security");', 'const security_1 = require("../core/security");\n' + import_str)

init_str = '        this.tokenStandards = new token_standards_1.TokenStandardsManager();\n        this.setupTokenRoutes();\n'
if 'this.tokenStandards' not in content:
    content = content.replace('this.setupCoreRoutes();', init_str + '        this.setupCoreRoutes();')

routes_code = """
    setupTokenRoutes() {
        // 1. POST /api/tokens/erc20/deploy
        this.app.post('/api/tokens/erc20/deploy', (req, res) => {
            try {
                const { name, symbol, decimals, totalSupply, deployer, deployerAddress } = req.body;
                if (!name || !symbol) {
                    res.status(400).json({ error: 'Name and symbol are required' });
                    return;
                }
                const token = this.tokenStandards.deployERC20(
                    name,
                    symbol,
                    decimals !== undefined ? decimals : 18,
                    totalSupply !== undefined ? totalSupply : 1000000,
                    deployer || deployerAddress || "0x0bfef9eb91a36d4010367869aa1e1927d353a35b"
                );
                res.json({
                    success: true,
                    contractAddress: token.address,
                    token
                });
            } catch (err) {
                res.status(400).json({ error: err.message });
            }
        });

        // 2. POST /api/tokens/erc20/transfer
        this.app.post('/api/tokens/erc20/transfer', (req, res) => {
            try {
                const { contractAddress, contract, from, to, amount, value } = req.body;
                const addr = contractAddress || contract;
                const amt = amount !== undefined ? amount : value;
                const result = this.tokenStandards.transfer(addr, from, to, amt);
                res.json(result);
            } catch (err) {
                res.status(400).json({ error: err.message });
            }
        });

        // 3. POST /api/tokens/erc20/approve
        this.app.post('/api/tokens/erc20/approve', (req, res) => {
            try {
                const { contractAddress, contract, owner, from, spender, amount, value } = req.body;
                const addr = contractAddress || contract;
                const own = owner || from;
                const amt = amount !== undefined ? amount : value;
                const result = this.tokenStandards.approve(addr, own, spender, amt);
                res.json(result);
            } catch (err) {
                res.status(400).json({ error: err.message });
            }
        });

        // 4. GET /api/tokens/erc20/:address/balance
        this.app.get('/api/tokens/erc20/:address/balance', (req, res) => {
            try {
                const contractAddress = req.params.address;
                const holder = req.query.holder || req.query.address || req.query.account;
                if (!holder) {
                    res.status(400).json({ error: "Missing holder query parameter" });
                    return;
                }
                const balance = this.tokenStandards.balanceOf(contractAddress, holder);
                res.json({
                    success: true,
                    contractAddress,
                    holder,
                    balance
                });
            } catch (err) {
                res.status(400).json({ error: err.message });
            }
        });

        // 5. GET /api/tokens/erc20/:address/info
        this.app.get('/api/tokens/erc20/:address/info', (req, res) => {
            try {
                const contractAddress = req.params.address;
                const token = this.tokenStandards.getContract(contractAddress);
                if (!token) {
                    res.status(404).json({ error: `Token contract ${contractAddress} not found` });
                    return;
                }
                res.json({
                    success: true,
                    address: token.address,
                    name: token.name,
                    symbol: token.symbol,
                    decimals: token.decimals,
                    totalSupply: token.totalSupply,
                    deployer: token.deployer,
                    type: token.type,
                    balancesCount: Object.keys(token.balances || {}).length,
                    eventsCount: token.events?.length || 0
                });
            } catch (err) {
                res.status(400).json({ error: err.message });
            }
        });

        // 6. POST /api/tokens/erc721/mint
        this.app.post('/api/tokens/erc721/mint', (req, res) => {
            try {
                const { contractAddress, contract, to, tokenId, tokenURI, uri, name, symbol, deployer, deployerAddress } = req.body;
                let addr = contractAddress || contract;

                if (!addr || !this.tokenStandards.getContract(addr)) {
                    if (name && symbol) {
                        const token721 = this.tokenStandards.deployERC721(name, symbol, deployer || deployerAddress || to);
                        addr = token721.address;
                    } else if (!addr) {
                        const token721 = this.tokenStandards.deployERC721("Verdis NFT", "VNFT", deployer || deployerAddress || to);
                        addr = token721.address;
                    }
                }

                const result = this.tokenStandards.mintERC721(addr, to, tokenId, tokenURI || uri || "");
                res.json(result);
            } catch (err) {
                res.status(400).json({ error: err.message });
            }
        });

        // 7. POST /api/tokens/erc721/transfer
        this.app.post('/api/tokens/erc721/transfer', (req, res) => {
            try {
                const { contractAddress, contract, spender, from, to, tokenId } = req.body;
                const addr = contractAddress || contract;
                const sp = spender || from;
                const result = this.tokenStandards.erc721TransferFrom(addr, sp, from, to, tokenId);
                res.json(result);
            } catch (err) {
                res.status(400).json({ error: err.message });
            }
        });

        // 8. GET /api/tokens/erc721/:contract/:tokenId
        this.app.get('/api/tokens/erc721/:contract/:tokenId', (req, res) => {
            try {
                const contractAddress = req.params.contract;
                const tokenId = req.params.tokenId;
                const owner = this.tokenStandards.ownerOf(contractAddress, tokenId);
                const uri = this.tokenStandards.tokenURI(contractAddress, tokenId);
                const approved = this.tokenStandards.getApproved(contractAddress, tokenId);

                res.json({
                    success: true,
                    contract: contractAddress,
                    tokenId,
                    owner,
                    tokenURI: uri,
                    approved
                });
            } catch (err) {
                res.status(404).json({ error: err.message });
            }
        });

        // 9. POST /api/tokens/erc1155/mint
        this.app.post('/api/tokens/erc1155/mint', (req, res) => {
            try {
                const { contractAddress, contract, to, id, tokenId, amount, value, data, uri, deployer, deployerAddress } = req.body;
                let addr = contractAddress || contract;
                const tId = id !== undefined ? id : tokenId;
                const amt = amount !== undefined ? amount : value;

                if (!addr || !this.tokenStandards.getContract(addr)) {
                    const token1155 = this.tokenStandards.deployERC1155(uri || "https://verdis.network/api/tokens/erc1155/{id}", deployer || deployerAddress || to);
                    addr = token1155.address;
                }

                const result = this.tokenStandards.mintERC1155(addr, to, tId, amt, data);
                res.json(result);
            } catch (err) {
                res.status(400).json({ error: err.message });
            }
        });

        // 10. POST /api/tokens/erc1155/batch-transfer
        this.app.post('/api/tokens/erc1155/batch-transfer', (req, res) => {
            try {
                const { contractAddress, contract, operator, from, to, ids, amounts, values, data } = req.body;
                const addr = contractAddress || contract;
                const op = operator || from;
                const amts = amounts || values;
                const result = this.tokenStandards.safeBatchTransferFrom(addr, op, from, to, ids, amts, data);
                res.json(result);
            } catch (err) {
                res.status(400).json({ error: err.message });
            }
        });

        // 11. GET /api/tokens/list
        this.app.get('/api/tokens/list', (req, res) => {
            try {
                const tokens = this.tokenStandards.listTokens();
                res.json({
                    success: true,
                    count: tokens.length,
                    tokens
                });
            } catch (err) {
                res.status(500).json({ error: err.message });
            }
        });
    }
"""

if 'setupTokenRoutes()' not in content:
    content = content.replace('    start(port) {', routes_code + '\n    start(port) {')

with open('/opt/verdis/app/dist/api/server.js', 'w') as f:
    f.write(content)
print("Successfully patched server.js")
