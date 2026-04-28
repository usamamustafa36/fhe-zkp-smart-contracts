// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IZKPVerifier
 * @dev Minimal interface to the auto-generated Groth16 verifier contract
 *      produced by `snarkjs generateverifier` from the range_commit circuit.
 *
 *      The full verifier contract is generated at build time
 *      (zkp_prod/scripts/build.sh) and deployed separately.
 *      FHESmartContract calls it via this interface so proof verification
 *      is enforced on-chain before any ciphertext is accepted.
 */
interface IZKPVerifier {
    /**
     * @dev Verify a Groth16 proof for the range-commitment circuit.
     * @param a   Proof element A (G1 point)
     * @param b   Proof element B (G2 point)
     * @param c   Proof element C (G1 point)
     * @param input Public signals: [commitment, contextHash]
     * @return True if the proof is valid.
     */
    function verifyProof(
        uint256[2]    calldata a,
        uint256[2][2] calldata b,
        uint256[2]    calldata c,
        uint256[2]    calldata input
    ) external view returns (bool);
}

/**
 * @title FHESmartContract
 * @dev Privacy-preserving computations using Fully Homomorphic Encryption.
 *      Enforces on-chain ZKP proof verification before accepting ciphertexts.
 *
 * Master's Thesis — Blockchain Integration for FHE
 */
contract FHESmartContract {

    // -------------------------------------------------------------------
    // ZKP verifier
    // -------------------------------------------------------------------

    /// @notice Address of the deployed Groth16 verifier contract.
    ///         Set to address(0) to disable proof enforcement (demo/test only).
    IZKPVerifier public zkpVerifier;

    /// @notice Replace the verifier contract (owner only).
    function setZKPVerifier(address verifier) external onlyOwner {
        zkpVerifier = IZKPVerifier(verifier);
    }
    
    // Events
    event FHEComputationSubmitted(
        bytes32 indexed computationId,
        address indexed submitter,
        uint8 operation,
        uint256 timestamp
    );

    /// @notice Emitted when an on-chain ZKP proof is verified successfully.
    ///         Records the commitment and context hash from the proof's public
    ///         signals, creating an immutable audit entry that proves the
    ///         submitted ciphertext was accompanied by a valid range proof.
    event ZKPVerified(
        bytes32 indexed computationId,
        uint256 commitment,
        uint256 contextHash,
        uint256 timestamp
    );

    event FHEComputationCompleted(
        bytes32 indexed computationId,
        bytes result,
        uint256 timestamp
    );

    event FHEComputationFailed(
        bytes32 indexed computationId,
        string reason,
        uint256 timestamp
    );
    
    // Structs
    struct Computation {
        bytes32 id;
        address submitter;
        bytes encryptedData;
        uint8 operation;
        bytes metadata;
        bytes result;
        ComputationStatus status;
        uint256 timestamp;
        uint256 completionTime;
    }
    
    // Enums
    enum ComputationStatus {
        Pending,
        Processing,
        Completed,
        Failed
    }
    
    enum OperationType {
        Add,
        Multiply,
        Aggregate
    }
    
    // State variables
    mapping(bytes32 => Computation) public computations;
    mapping(address => bytes32[]) public userComputations;
    bytes32[] public allComputations;
    
    // Access control
    address public owner;
    mapping(address => bool) public authorizedComputers;
    
    // Statistics
    uint256 public totalComputations;
    uint256 public completedComputations;
    uint256 public failedComputations;
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyAuthorizedComputer() {
        require(authorizedComputers[msg.sender], "Only authorized computers can call this function");
        _;
    }
    
    modifier computationExists(bytes32 computationId) {
        require(computations[computationId].id != bytes32(0), "Computation does not exist");
        _;
    }
    
    // Constructor
    constructor() {
        owner = msg.sender;
        authorizedComputers[msg.sender] = true;
    }
    
    /**
     * @dev Submit FHE computation to the blockchain.
     *
     *      If a ZKP verifier contract is configured (zkpVerifier != address(0)),
     *      the caller must supply a valid Groth16 proof from the range_commit
     *      circuit.  The proof is verified on-chain before the ciphertext is
     *      accepted, enforcing that the encrypted input satisfies the declared
     *      validity constraints without revealing the plaintext value.
     *
     *      When zkpVerifier == address(0) (e.g., local/test deployments),
     *      proof enforcement is skipped and the function behaves as a simple
     *      ciphertext registry.
     *
     * @param encryptedData The FHE ciphertext of the validated input.
     * @param operation     Operation type: 0=Add, 1=Multiply, 2=Aggregate.
     * @param metadata      Arbitrary metadata (e.g., request ID, version).
     * @param proofA        Groth16 proof element A (G1). Pass [0,0] if no verifier.
     * @param proofB        Groth16 proof element B (G2). Pass [[0,0],[0,0]] if no verifier.
     * @param proofC        Groth16 proof element C (G1). Pass [0,0] if no verifier.
     * @param publicSignals Public inputs [commitment, contextHash] for the ZKP.
     * @return computationId Unique identifier for this computation record.
     */
    function submitFHEComputation(
        bytes calldata encryptedData,
        uint8 operation,
        bytes calldata metadata,
        uint256[2]    calldata proofA,
        uint256[2][2] calldata proofB,
        uint256[2]    calldata proofC,
        uint256[2]    calldata publicSignals
    ) external returns (bytes32 computationId) {
        require(encryptedData.length > 0, "Encrypted data cannot be empty");
        require(operation <= 2, "Invalid operation type"); // 0=Add, 1=Multiply, 2=Aggregate

        // On-chain ZKP verification — enforces input validity without
        // revealing the plaintext value.
        if (address(zkpVerifier) != address(0)) {
            require(
                zkpVerifier.verifyProof(proofA, proofB, proofC, publicSignals),
                "ZKP proof verification failed: input does not satisfy constraints"
            );
        }

        // Compute the computation ID first so we can emit ZKPVerified with it.
        // block.prevrandao (EIP-4399) replaces the deprecated block.difficulty
        // after The Merge; it provides the RANDAO reveal as a source of
        // per-block randomness on post-Merge Ethereum networks.
        computationId = keccak256(
            abi.encodePacked(
                msg.sender,
                encryptedData,
                operation,
                metadata,
                block.timestamp,
                block.prevrandao
            )
        );

        require(computations[computationId].id == bytes32(0), "Computation ID collision");

        // Emit ZKP verification event — creates an immutable on-chain record
        // that proof verification passed for this computation.
        if (address(zkpVerifier) != address(0)) {
            emit ZKPVerified(computationId, publicSignals[0], publicSignals[1], block.timestamp);
        }
        
        // Create computation record
        computations[computationId] = Computation({
            id: computationId,
            submitter: msg.sender,
            encryptedData: encryptedData,
            operation: operation,
            metadata: metadata,
            result: "",
            status: ComputationStatus.Pending,
            timestamp: block.timestamp,
            completionTime: 0
        });
        
        // Update mappings
        userComputations[msg.sender].push(computationId);
        allComputations.push(computationId);
        totalComputations++;
        
        emit FHEComputationSubmitted(
            computationId,
            msg.sender,
            operation,
            block.timestamp
        );
        
        return computationId;
    }
    
    /**
     * @dev Process FHE computation (called by authorized computers)
     * @param computationId The computation to process
     * @param result The encrypted result of the computation
     */
    function processFHEComputation(
        bytes32 computationId,
        bytes calldata result
    ) external onlyAuthorizedComputer computationExists(computationId) {
        Computation storage computation = computations[computationId];
        
        require(computation.status == ComputationStatus.Pending, "Computation not pending");
        
        // Update computation status
        computation.status = ComputationStatus.Processing;
        
        // In a real implementation, this is where the actual FHE computation would happen
        // For now, we'll simulate the computation and store the result
        
        // Simulate computation time
        // In practice, this would be done off-chain by authorized computers
        
        // Update computation with result
        computation.result = result;
        computation.status = ComputationStatus.Completed;
        computation.completionTime = block.timestamp;
        
        completedComputations++;
        
        emit FHEComputationCompleted(
            computationId,
            result,
            block.timestamp
        );
    }
    
    /**
     * @dev Mark computation as failed
     * @param computationId The computation to mark as failed
     * @param reason The reason for failure
     */
    function markComputationFailed(
        bytes32 computationId,
        string calldata reason
    ) external onlyAuthorizedComputer computationExists(computationId) {
        Computation storage computation = computations[computationId];
        
        require(computation.status == ComputationStatus.Pending || 
                computation.status == ComputationStatus.Processing, 
                "Computation cannot be marked as failed");
        
        computation.status = ComputationStatus.Failed;
        computation.completionTime = block.timestamp;
        
        failedComputations++;
        
        emit FHEComputationFailed(
            computationId,
            reason,
            block.timestamp
        );
    }
    
    /**
     * @dev Get computation result
     * @param computationId The computation ID
     * @return result The encrypted result
     */
    function getComputationResult(
        bytes32 computationId
    ) external view computationExists(computationId) returns (bytes memory result) {
        Computation storage computation = computations[computationId];
        
        require(computation.status == ComputationStatus.Completed, "Computation not completed");
        
        return computation.result;
    }
    
    /**
     * @dev Get computation status
     * @param computationId The computation ID
     * @return status The computation status
     */
    function getComputationStatus(
        bytes32 computationId
    ) external view computationExists(computationId) returns (uint8 status) {
        return uint8(computations[computationId].status);
    }
    
    /**
     * @dev Get computation details
     * @param computationId The computation ID
     * @return Computation struct with all details
     */
    function getComputation(
        bytes32 computationId
    ) external view computationExists(computationId) returns (Computation memory) {
        return computations[computationId];
    }
    
    /**
     * @dev Get user's computations
     * @param user The user address
     * @return Array of computation IDs
     */
    function getUserComputations(
        address user
    ) external view returns (bytes32[] memory) {
        return userComputations[user];
    }
    
    /**
     * @dev Get all computations
     * @return Array of all computation IDs
     */
    function getAllComputations() external view returns (bytes32[] memory) {
        return allComputations;
    }
    
    /**
     * @dev Add authorized computer
     * @param computer The computer address to authorize
     */
    function addAuthorizedComputer(address computer) external onlyOwner {
        require(computer != address(0), "Invalid computer address");
        authorizedComputers[computer] = true;
    }
    
    /**
     * @dev Remove authorized computer
     * @param computer The computer address to remove
     */
    function removeAuthorizedComputer(address computer) external onlyOwner {
        authorizedComputers[computer] = false;
    }
    
    /**
     * @dev Get contract statistics
     * @return total Total computations
     * @return completed Completed computations
     * @return failed Failed computations
     */
    function getStatistics() external view returns (uint256 total, uint256 completed, uint256 failed) {
        return (totalComputations, completedComputations, failedComputations);
    }
    
    /**
     * @dev Check if address is authorized computer
     * @param computer The computer address to check
     * @return bool True if authorized
     */
    function isAuthorizedComputer(address computer) external view returns (bool) {
        return authorizedComputers[computer];
    }
    
    /**
     * @dev Transfer ownership
     * @param newOwner The new owner address
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid new owner");
        owner = newOwner;
    }
    
    /**
     * @dev Emergency function to pause contract (if needed)
     */
    function emergencyPause() external onlyOwner {
        // In a real implementation, you might want to add a pause mechanism
        // This is a placeholder for emergency functionality
    }
} 