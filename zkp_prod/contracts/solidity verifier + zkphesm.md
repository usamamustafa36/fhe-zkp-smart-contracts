// SPDX-License-Identifier: GPL-3.0
/*
    Copyright 2021 0KIMS association.

    This file is generated with [snarkJS](https://github.com/iden3/snarkjs).

    snarkJS is a free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    snarkJS is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
    License for more details.

    You should have received a copy of the GNU General Public License
    along with snarkJS. If not, see <https://www.gnu.org/licenses/>.
*/

pragma solidity >=0.7.0 <0.9.0;

contract Groth16Verifier {
    // Scalar field size
    uint256 constant r    = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
    // Base field size
    uint256 constant q   = 21888242871839275222246405745257275088696311157297823662689037894645226208583;

    // Verification Key data
    uint256 constant alphax  = 20491192805390485299153009773594534940189261866228447918068658471970481763042;
    uint256 constant alphay  = 9383485363053290200918347156157836566562967994039712273449902621266178545958;
    uint256 constant betax1  = 4252822878758300859123897981450591353533073413197771768651442665752259397132;
    uint256 constant betax2  = 6375614351688725206403948262868962793625744043794305715222011528459656738731;
    uint256 constant betay1  = 21847035105528745403288232691147584728191162732299865338377159692350059136679;
    uint256 constant betay2  = 10505242626370262277552901082094356697409835680220590971873171140371331206856;
    uint256 constant gammax1 = 11559732032986387107991004021392285783925812861821192530917403151452391805634;
    uint256 constant gammax2 = 10857046999023057135944570762232829481370756359578518086990519993285655852781;
    uint256 constant gammay1 = 4082367875863433681332203403145435568316851327593401208105741076214120093531;
    uint256 constant gammay2 = 8495653923123431417604973247489272438418190587263600148770280649306958101930;
    uint256 constant deltax1 = 8324886241956710282030050773020908332674510989088419884708694891769113564364;
    uint256 constant deltax2 = 12009076955521828483063994347385998841889038803431664447932255686299096325570;
    uint256 constant deltay1 = 7407041228935260086984014621211668682063045126265426487763993580005445845571;
    uint256 constant deltay2 = 21124209619806596336177186937890607112411453977802539210036497088617594862603;

    
    uint256 constant IC0x = 14085014449362165865952918517816070603830648612711828828513318299831624958557;
    uint256 constant IC0y = 7519714779535775818726323568662861386056331369887048405490750388433899298917;
    
    uint256 constant IC1x = 21001379435081736145202809206238294500393515141795130199585704440600350675155;
    uint256 constant IC1y = 21266628917985380224819125231951271669003564369622515184460850865787104637700;
    
    uint256 constant IC2x = 4109231822829873229421055697448123545807184953965652597149227240805508662015;
    uint256 constant IC2y = 20485296403046535417128952289324289325506622981655157970961501321248433000503;
    
 
    // Memory data
    uint16 constant pVk = 0;
    uint16 constant pPairing = 128;

    uint16 constant pLastMem = 896;

    function verifyProof(uint[2] calldata _pA, uint[2][2] calldata _pB, uint[2] calldata _pC, uint[2] calldata _pubSignals) public view returns (bool) {
        assembly {
            function checkField(v) {
                if iszero(lt(v, r)) {
                    mstore(0, 0)
                    return(0, 0x20)
                }
            }
            
            // G1 function to multiply a G1 value(x,y) to value in an address
            function g1_mulAccC(pR, x, y, s) {
                let success
                let mIn := mload(0x40)
                mstore(mIn, x)
                mstore(add(mIn, 32), y)
                mstore(add(mIn, 64), s)

                success := staticcall(sub(gas(), 2000), 7, mIn, 96, mIn, 64)

                if iszero(success) {
                    mstore(0, 0)
                    return(0, 0x20)
                }

                mstore(add(mIn, 64), mload(pR))
                mstore(add(mIn, 96), mload(add(pR, 32)))

                success := staticcall(sub(gas(), 2000), 6, mIn, 128, pR, 64)

                if iszero(success) {
                    mstore(0, 0)
                    return(0, 0x20)
                }
            }

            function checkPairing(pA, pB, pC, pubSignals, pMem) -> isOk {
                let _pPairing := add(pMem, pPairing)
                let _pVk := add(pMem, pVk)

                mstore(_pVk, IC0x)
                mstore(add(_pVk, 32), IC0y)

                // Compute the linear combination vk_x
                
                g1_mulAccC(_pVk, IC1x, IC1y, calldataload(add(pubSignals, 0)))
                
                g1_mulAccC(_pVk, IC2x, IC2y, calldataload(add(pubSignals, 32)))
                

                // -A
                mstore(_pPairing, calldataload(pA))
                mstore(add(_pPairing, 32), mod(sub(q, calldataload(add(pA, 32))), q))

                // B
                mstore(add(_pPairing, 64), calldataload(pB))
                mstore(add(_pPairing, 96), calldataload(add(pB, 32)))
                mstore(add(_pPairing, 128), calldataload(add(pB, 64)))
                mstore(add(_pPairing, 160), calldataload(add(pB, 96)))

                // alpha1
                mstore(add(_pPairing, 192), alphax)
                mstore(add(_pPairing, 224), alphay)

                // beta2
                mstore(add(_pPairing, 256), betax1)
                mstore(add(_pPairing, 288), betax2)
                mstore(add(_pPairing, 320), betay1)
                mstore(add(_pPairing, 352), betay2)

                // vk_x
                mstore(add(_pPairing, 384), mload(add(pMem, pVk)))
                mstore(add(_pPairing, 416), mload(add(pMem, add(pVk, 32))))


                // gamma2
                mstore(add(_pPairing, 448), gammax1)
                mstore(add(_pPairing, 480), gammax2)
                mstore(add(_pPairing, 512), gammay1)
                mstore(add(_pPairing, 544), gammay2)

                // C
                mstore(add(_pPairing, 576), calldataload(pC))
                mstore(add(_pPairing, 608), calldataload(add(pC, 32)))

                // delta2
                mstore(add(_pPairing, 640), deltax1)
                mstore(add(_pPairing, 672), deltax2)
                mstore(add(_pPairing, 704), deltay1)
                mstore(add(_pPairing, 736), deltay2)


                let success := staticcall(sub(gas(), 2000), 8, _pPairing, 768, _pPairing, 0x20)

                isOk := and(success, mload(_pPairing))
            }

            let pMem := mload(0x40)
            mstore(0x40, add(pMem, pLastMem))

            // Validate that all evaluations ∈ F
            
            checkField(calldataload(add(_pubSignals, 0)))
            
            checkField(calldataload(add(_pubSignals, 32)))
            

            // Validate all evaluations
            let isValid := checkPairing(_pA, _pB, _pC, _pubSignals, pMem)

            mstore(0, isValid)
             return(0, 0x20)
         }
     }
 }


------------------------------------------------------------------------------------------------------------------------------------------------------------------------




// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/*
 * ZKP-Enhanced FHE Smart Contract
 * ================================
 * 
 * Integrates production-grade ZKP range proofs with FHE computation pipeline.
 * 
 * UPGRADE: Replaces abstracted ZKP validation with cryptographic Groth16 SNARKs.
 * 
 * FEATURES:
 * - On-chain ZKP proof verification (Groth16)
 * - Commitment-based anti-replay protection
 * - Context binding (chainId, contract, operation, request)
 * - FHE ciphertext storage and computation tracking
 * 
 * WORKFLOW:
 * 1. User generates ZKP proof off-chain (proves 0 <= x <= 1,000,000)
 * 2. User submits proof + commitment + FHE ciphertext
 * 3. Contract verifies ZKP proof on-chain
 * 4. Contract checks commitment not reused (anti-replay)
 * 5. Contract stores FHE computation request
 * 6. Off-chain worker processes FHE computation
 * 7. Result submitted back on-chain
 * 
 * SECURITY:
 * - Cryptographic soundness: Cannot forge proofs for invalid x
 * - Anti-replay: Commitment tracking prevents proof reuse
 * - Context binding: Proofs only valid for specific chain/contract/request
 * 
 * THESIS REFERENCE: Chapter 4, Section 4.2 - Smart Contract Integration
 */

interface IGroth16Verifier {
    function verifyProof(
        uint[2] calldata _pA,
        uint[2][2] calldata _pB,
        uint[2] calldata _pC,
        uint[2] calldata _pubSignals
    ) external view returns (bool);
}

contract ZKPFHESmartContract {
    
    // =========================================================================
    // STATE VARIABLES
    // =========================================================================
    
    /// @notice Groth16 verifier contract (generated by snarkjs)
    IGroth16Verifier public immutable zkpVerifier;
    
    /// @notice Contract owner (can update settings)
    address public owner;
    
    /// @notice Used commitments for anti-replay protection
    /// @dev Maps commitment hash to usage status
    mapping(bytes32 => bool) public usedCommitments;
    
    /// @notice Computation storage
    struct Computation {
        uint256 id;
        bytes32 commitment;
        bytes32 contextHash;
        bytes encryptedData;
        address submitter;
        uint256 timestamp;
        ComputationStatus status;
        bytes result;
    }
    
    enum ComputationStatus {
        Pending,
        Processing,
        Completed,
        Failed
    }
    
    /// @notice All computations
    mapping(uint256 => Computation) public computations;
    uint256 public computationCount;
    
    // =========================================================================
    // EVENTS
    // =========================================================================
    
    event ProofVerified(
        bytes32 indexed commitmentHash,
        bytes32 indexed contextHash,
        address indexed submitter
    );
    
    event ComputationSubmitted(
        uint256 indexed computationId,
        bytes32 commitment,
        address submitter,
        uint256 timestamp
    );
    
    event ComputationCompleted(
        uint256 indexed computationId,
        bytes32 resultHash
    );
    
    // =========================================================================
    // CONSTRUCTOR
    // =========================================================================
    
    constructor(address _verifierAddress) {
        require(_verifierAddress != address(0), "Invalid verifier address");
        zkpVerifier = IGroth16Verifier(_verifierAddress);
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    // =========================================================================
    // MAIN FUNCTIONS
    // =========================================================================
    
    /**
     * @notice Submit FHE computation with ZKP range proof
     * @param _pA Groth16 proof component A
     * @param _pB Groth16 proof component B
     * @param _pC Groth16 proof component C
     * @param _commitment Public commitment (binds proof to context)
     * @param _contextHash Context binding hash
     * @param _encryptedData FHE ciphertext to compute on
     * @return computationId Unique computation identifier
     * 
     * SECURITY:
     * - Verifies ZKP proof cryptographically
     * - Checks commitment not reused (anti-replay)
     * - Validates context binding
     */
    function submitComputationWithProof(
        uint[2] calldata _pA,
        uint[2][2] calldata _pB,
        uint[2] calldata _pC,
        uint256 _commitment,
        uint256 _contextHash,
        bytes calldata _encryptedData
    ) external returns (uint256 computationId) {
        
        // 1. Verify ZKP proof on-chain
        uint[2] memory publicSignals = [_commitment, _contextHash];
        
        require(
            zkpVerifier.verifyProof(_pA, _pB, _pC, publicSignals),
            "ZKP proof verification failed"
        );
        
        // 2. Check commitment not reused (anti-replay protection)
        bytes32 commitmentHash = keccak256(
            abi.encodePacked(_commitment, _contextHash)
        );
        
        require(
            !usedCommitments[commitmentHash],
            "Commitment already used (replay attack)"
        );
        
        usedCommitments[commitmentHash] = true;
        
        // 3. Verify context binding matches this transaction
        bytes32 expectedContextHash = computeContextHash(
            block.chainid,
            address(this),
            0,  // opType: 0 = validate
            computationCount  // Use computationCount as requestId
        );
        
        require(
            uint256(expectedContextHash) == _contextHash,
            "Context hash mismatch"
        );
        
        // 4. Store computation
        computationId = computationCount++;
        
        computations[computationId] = Computation({
            id: computationId,
            commitment: bytes32(_commitment),
            contextHash: bytes32(_contextHash),
            encryptedData: _encryptedData,
            submitter: msg.sender,
            timestamp: block.timestamp,
            status: ComputationStatus.Pending,
            result: ""
        });
        
        emit ProofVerified(commitmentHash, bytes32(_contextHash), msg.sender);
        emit ComputationSubmitted(computationId, bytes32(_commitment), msg.sender, block.timestamp);
    }
    
    /**
     * @notice Submit computation result (called by authorized worker)
     * @param _computationId Computation identifier
     * @param _result Encrypted result
     */
    function submitResult(
        uint256 _computationId,
        bytes calldata _result
    ) external onlyOwner {
        require(_computationId < computationCount, "Invalid computation ID");
        
        Computation storage comp = computations[_computationId];
        require(comp.status == ComputationStatus.Pending, "Already processed");
        
        comp.result = _result;
        comp.status = ComputationStatus.Completed;
        
        emit ComputationCompleted(_computationId, keccak256(_result));
    }
    
    // =========================================================================
    // HELPER FUNCTIONS
    // =========================================================================
    
    /**
     * @notice Compute context hash on-chain
     * @dev Must match off-chain computation in Python
     * 
     * SPECIFICATION:
     *   contextHash = keccak256(chainId || contractAddr || opType || requestId)
     * 
     * ANTI-REPLAY PROPERTIES:
     * - chainId: Prevents cross-chain replay
     * - contractAddr: Prevents cross-contract replay
     * - opType: Prevents operation type confusion
     * - requestId: Prevents same-context replay
     */
    function computeContextHash(
        uint256 _chainId,
        address _contractAddr,
        uint8 _opType,
        uint256 _requestId
    ) public pure returns (bytes32) {
        return keccak256(
            abi.encodePacked(
                _chainId,
                _contractAddr,
                _opType,
                _requestId
            )
        );
    }
    
    /**
     * @notice Get computation details
     */
    function getComputation(uint256 _computationId)
        external
        view
        returns (
            bytes32 commitment,
            bytes32 contextHash,
            bytes memory encryptedData,
            address submitter,
            uint256 timestamp,
            ComputationStatus status,
            bytes memory result
        )
    {
        require(_computationId < computationCount, "Invalid computation ID");
        Computation storage comp = computations[_computationId];
        
        return (
            comp.commitment,
            comp.contextHash,
            comp.encryptedData,
            comp.submitter,
            comp.timestamp,
            comp.status,
            comp.result
        );
    }
    
    /**
     * @notice Check if commitment has been used
     */
    function isCommitmentUsed(bytes32 _commitmentHash) external view returns (bool) {
        return usedCommitments[_commitmentHash];
    }
}
