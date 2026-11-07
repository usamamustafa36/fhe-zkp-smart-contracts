pragma circom 2.1.6;

include "circomlib/circuits/poseidon.circom";
include "circomlib/circuits/comparators.circom";
include "circomlib/circuits/bitify.circom";

/*
 * Range Commitment Proof for Production ZKP
 * ==========================================
 * 
 * PURPOSE:
 *   Prove that a secret value x is within valid range [0, 1,000,000]
 *   while binding it to a specific execution context via commitment.
 *
 * PRIVATE INPUTS:
 *   x        : The secret value to validate (must be 0 <= x <= 1,000,000)
 *   salt     : Random salt for commitment hiding (prevents brute-force)
 *
 * PUBLIC INPUTS:
 *   commitment  : Poseidon(x, salt, contextHash) - binds x to context
 *   contextHash : Poseidon(chainId, contractAddr, opType, requestId)
 *
 * CONSTRAINTS:
 *   1. Range Proof: Proves 0 <= x <= 1,000,000
 *   2. Commitment Binding: commitment = Poseidon(x, salt, contextHash)
 *
 * SECURITY PROPERTIES:
 *   - Completeness: Valid x always produces accepting proof
 *   - Soundness: Invalid x cannot produce accepting proof (cryptographic)
 *   - Zero-Knowledge: Proof reveals nothing about x (only that it's in range)
 *   - Binding: Commitment fixes x to specific context (anti-replay)
 *   - Hiding: Salt prevents x recovery from commitment (brute-force protection)
 *
 * ANTI-REPLAY PROTECTION:
 *   contextHash includes:
 *   - chainId: Prevents cross-chain replay
 *   - contractAddr: Prevents cross-contract replay  
 *   - opType: Prevents operation type confusion
 *   - requestId: Prevents same-request replay (timestamp-based)
 *
 * THESIS UPGRADE:
 *   This replaces the abstracted ZKP oracle with production-grade
 *   cryptographic SNARKs suitable for mainnet deployment.
 *
 * REFERENCE:
 *   - crypto/threat_model.md - Updated ZKP adversary model
 *   - docs/limitations.md - Groth16 trusted setup caveat
 */

template RangeCommitment() {
    // =========================================================================
    // SIGNAL DECLARATIONS
    // =========================================================================
    
    // Private inputs (witness - never revealed)
    signal input x;
    signal input salt;
    
    // Public inputs (visible on-chain)
    signal input commitment;
    signal input contextHash;
    
    // =========================================================================
    // CONSTRAINT 1: Range Proof (0 <= x <= 1,000,000)
    // =========================================================================
    
    /*
     * Range check using comparator circuit.
     * 
     * We need to prove: 0 <= x <= 1,000,000
     * 
     * In field arithmetic over BN254 there are no negative numbers:
     * a "negative" value such as -1 is the field element p - 1.
     * LessEqThan(n) is only sound when both inputs are already known
     * to fit in n bits. Without that, x = p - 1 passes the comparison.
     * So we first constrain x to 32 bits (0 <= x < 2^32), then
     * check x <= 1,000,000.
     */
    
    component xBits = Num2Bits(32);
    xBits.in <== x;
    
    component isLessThanOrEqual = LessEqThan(32);
    isLessThanOrEqual.in[0] <== x;
    isLessThanOrEqual.in[1] <== 1000000;
    
    // Assert comparison result is 1 (true)
    isLessThanOrEqual.out === 1;
    
    // =========================================================================
    // CONSTRAINT 2: Commitment Binding
    // =========================================================================
    
    /*
     * Commitment scheme: Poseidon(x, salt, contextHash)
     * 
     * Properties:
     * - Binding: Cannot find x' != x with same commitment
     * - Hiding: Cannot recover x from commitment (requires salt)
     * - Collision-resistant: Poseidon is cryptographic hash
     *
     * Context binding ensures proof is only valid for:
     * - Specific blockchain (chainId)
     * - Specific contract (contractAddr)
     * - Specific operation (opType)
     * - Specific request (requestId - unique per submission)
     */
    
    component commitmentHasher = Poseidon(3);
    commitmentHasher.inputs[0] <== x;
    commitmentHasher.inputs[1] <== salt;
    commitmentHasher.inputs[2] <== contextHash;
    
    // Assert computed commitment matches public input
    // This binds the proof to the declared commitment
    commitment === commitmentHasher.out;
}

// Main component: specify which signals are public
// All others (x, salt) remain private (zero-knowledge)
component main {public [commitment, contextHash]} = RangeCommitment();
