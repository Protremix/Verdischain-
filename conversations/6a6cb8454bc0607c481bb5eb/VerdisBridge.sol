// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Verdis Bridge
 * @notice Locks wVRS on BSC for redemption back to VRS on Verdis chain
 * @dev Bridge operator monitors Verdis chain for lock events and mints wVRS on BSC
 */
interface IWVRS {
    function mint(address to, uint256 amount) external;
    function burn(uint256 amount) external;
}

contract VerdisBridge {
    IWVRS public immutable wvrs;
    address public operator;
    
    struct PendingMint {
        address to;
        uint256 amount;
        uint256 timestamp;
        bool executed;
    }
    
    mapping(bytes32 => PendingMint) public pendingMints;
    mapping(address => uint256) public lockedAmounts;
    
    event LockOnVerdis(address indexed user, uint256 amount, bytes32 indexed mintId);
    event MintOnBSC(bytes32 indexed mintId, address indexed to, uint256 amount);
    event BurnForRedeem(address indexed user, uint256 amount, bytes32 indexed redeemId);
    event UnlockOnVerdis(bytes32 indexed redeemId, address indexed user, uint256 amount);
    
    modifier onlyOperator() {
        require(msg.sender == operator, "Only operator");
        _;
    }
    
    constructor(address _wvrs) {
        wvrs = IWVRS(_wvrs);
        operator = msg.sender;
    }
    
    // Operator calls this after verifying VRS was locked on Verdis chain
    function mintOnBSC(bytes32 mintId, address to, uint256 amount) external onlyOperator {
        require(!pendingMints[mintId].executed, "Already executed");
        pendingMints[mintId] = PendingMint(to, amount, block.timestamp, true);
        wvrs.mint(to, amount);
        emit MintOnBSC(mintId, to, amount);
    }
    
    // User burns wVRS to redeem back to VRS on Verdis chain
    function redeemToVerdis(uint256 amount) external returns (bytes32 redeemId) {
        require(amount > 0, "Zero amount");
        redeemId = keccak256(abi.encodePacked(msg.sender, amount, block.timestamp));
        wvrs.burn(amount);
        emit BurnForRedeem(msg.sender, amount, redeemId);
        // Operator monitors this event and unlocks VRS on Verdis chain
    }
    
    function setOperator(address newOperator) external onlyOperator {
        operator = newOperator;
    }
}
