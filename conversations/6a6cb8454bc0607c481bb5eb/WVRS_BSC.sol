// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Wrapped Verdis (wVRS)
 * @notice ERC-20 token representing VRS on the BSC network
 * @dev 1 wVRS = 1 VRS. Mintable by bridge operator, burnable on redemption.
 */
contract WrappedVerdis {
    string public constant name = "Wrapped Verdis";
    string public constant symbol = "wVRS";
    uint8 public constant decimals = 18;
    uint256 public totalSupply;
    
    address public bridgeOperator;
    address public pendingBridgeOperator;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Mint(address indexed to, uint256 value);
    event Burn(address indexed from, uint256 value);
    event BridgeOperatorChanged(address indexed oldOperator, address indexed newOperator);
    
    modifier onlyBridge() {
        require(msg.sender == bridgeOperator, "Only bridge operator");
        _;
    }
    
    constructor() {
        bridgeOperator = msg.sender;
        emit BridgeOperatorChanged(address(0), msg.sender);
    }
    
    // Bridge: mint wVRS when VRS is locked on Verdis chain
    function mint(address to, uint256 amount) external onlyBridge {
        totalSupply += amount;
        balanceOf[to] += amount;
        emit Mint(to, amount);
        emit Transfer(address(0), to, amount);
    }
    
    // Bridge: burn wVRS when user redeems back to VRS on Verdis chain
    function burn(uint256 amount) external {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        totalSupply -= amount;
        emit Burn(msg.sender, amount);
        emit Transfer(msg.sender, address(0), amount);
    }
    
    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }
    
    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }
    
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(allowance[from][msg.sender] >= amount, "Insufficient allowance");
        require(balanceOf[from] >= amount, "Insufficient balance");
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        emit Transfer(from, to, amount);
        return true;
    }
    
    function proposeBridgeOperator(address newOperator) external onlyBridge {
        pendingBridgeOperator = newOperator;
    }
    
    function acceptBridgeOperator() external {
        require(msg.sender == pendingBridgeOperator, "Not pending operator");
        emit BridgeOperatorChanged(bridgeOperator, pendingBridgeOperator);
        bridgeOperator = pendingBridgeOperator;
        delete pendingBridgeOperator;
    }
}
