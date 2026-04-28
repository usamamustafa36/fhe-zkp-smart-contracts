# Threat Model - Privacy-Preserving Smart Contracts

**THESIS REFERENCE**: Chapter 3, Section 3.3 - Security Model and Assumptions

**FORMAL CRYPTOGRAPHIC ANALYSIS**: For rigorous definitions, proofs, and formal security model:
- **`crypto_theory/security_model.md`** - Formal adversary model, security definitions, cryptographic games
- **`crypto_theory/composition_analysis.md`** - Security reductions, proof sketches, composition theorem
- **`crypto_theory/leakage_model.md`** - Explicit leakage function ℒ, information-theoretic analysis
- **`crypto_theory/correctness_theorem.md`** - CKKS approximate correctness with error bounds

This document provides an **engineering-focused** threat analysis. The `crypto_theory/` directory provides **PhD-level formal cryptographic analysis** suitable for publication.

---

## 1. Adversary Types

### 1.1 Honest-but-Curious Peers
- **Description**: Network participants who follow the protocol correctly but attempt to learn private information from observations
- **Capabilities**: 
  - Access to all blockchain data (encrypted ciphertexts, transaction metadata)
  - Cannot decrypt FHE ciphertexts without keys
  - Can observe timing, sizes, and patterns
- **Protected Against**: ✅ Yes (via FHE encryption)

### 1.2 Blockchain Observers
- **Description**: External parties monitoring blockchain state
- **Capabilities**:
  - Read all on-chain data
  - Analyze transaction patterns
  - Cannot modify or inject data
- **Protected Against**: ✅ Yes (computational privacy via FHE)

### 1.3 Malicious Users (Limited Scope)
- **Description**: Users attempting to submit invalid inputs
- **Capabilities**:
  - Submit out-of-range or malformed inputs
  - Attempt to bypass validation
- **Protected Against**: ⚠️ Partial (via abstracted ZKP oracle)
- **Limitation**: See Section 4 - oracle is not cryptographically binding

---

## 2. Trust Assumptions

### 2.1 Trusted FHE Key Holder
- **Assumption**: The entity holding FHE private keys is trusted to:
  - Not decrypt intermediate computations unnecessarily
  - Properly manage key material
  - Decrypt only authorized results
- **Justification**: Single-key FHE inherently requires trust in decryptor
- **Future Work**: Threshold FHE or multi-party key management

### 2.2 Trusted Off-Chain Computation
- **Assumption**: FHE computations are performed correctly off-chain
- **Impact**: Results cannot be independently verified on-chain
- **Rationale**: On-chain FHE verification would require decryption (defeating privacy)
- **Mitigation**: Deterministic computation + audit logging

### 2.3 Honest ZKP Oracle (Abstracted)
- **Assumption**: Input validation oracle behaves honestly
- **Critical Limitation**: This is an **abstracted oracle**, NOT cryptographic ZKP
- **Impact**: Malicious prover could bypass validation in production deployment
- **Thesis Scope**: Demonstration of concept, not production cryptography
- **See**: `crypto/zkp_validator.py` header documentation

---

## 3. Protected Assets

### 3.1 Input Confidentiality
- **Guarantee**: Input values remain encrypted during submission
- **Mechanism**: FHE encryption before blockchain submission
- **Adversary**: Protected from blockchain observers and honest-but-curious peers

### 3.2 Computation Privacy
- **Guarantee**: Intermediate computation states remain encrypted
- **Mechanism**: Homomorphic operations on encrypted data
- **Limitation**: Computation operator (off-chain) can observe metadata

### 3.3 Result Confidentiality
- **Guarantee**: Results remain encrypted until authorized decryption
- **Mechanism**: FHE ciphertext output
- **Access Control**: Only key holder can decrypt

### 3.4 Audit Trail Integrity
- **Guarantee**: All operations logged immutably
- **Mechanism**: Transparent encrypted logging + blockchain anchoring
- **Adversary**: Protected from tampering (blockchain immutability)

---

## 4. Excluded Threats (Out of Scope)

### 4.1 Malicious Prover Attacks
- **Threat**: Adversary generates false ZKP proofs
- **Status**: ❌ NOT PROTECTED
- **Reason**: ZKP is abstracted oracle, not cryptographic implementation
- **Impact**: Production deployment requires real ZKP library
- **See**: `docs/limitations.md` Section 3

### 4.2 Side-Channel Attacks
- **Threat**: Timing attacks, power analysis, cache attacks
- **Status**: ❌ NOT PROTECTED
- **Reason**: No constant-time implementations or hardware isolation
- **Impact**: Information leakage in adversarial execution environments
- **Mitigation**: Requires specialized hardening (out of thesis scope)

### 4.3 Quantum Adversaries
- **Threat**: Quantum computers breaking FHE hardness assumptions
- **Status**: ❌ NOT PROTECTED
- **Reason**: Current FHE schemes (CKKS/BFV) not quantum-resistant
- **Impact**: Long-term confidentiality not guaranteed
- **Future Work**: Post-quantum FHE schemes

### 4.4 Denial of Service
- **Threat**: Resource exhaustion attacks on computation or blockchain
- **Status**: ❌ NOT PROTECTED
- **Reason**: No rate limiting or resource quotas implemented
- **Impact**: System availability not guaranteed under attack
- **Mitigation**: Requires production-grade infrastructure

### 4.5 Smart Contract Vulnerabilities
- **Threat**: Re-entrancy, integer overflow, etc. in Solidity contract
- **Status**: ⚠️ BASIC PROTECTION
- **Reason**: Standard Solidity 0.8+ protections, but not formally verified
- **Mitigation**: Requires formal verification (e.g., Certora, K framework)

---

## 5. Security Guarantees Summary

| Asset | Guarantee Level | Mechanism | Limitation |
|-------|----------------|-----------|------------|
| Input Privacy | ✅ High | FHE encryption | Key holder trust |
| Computation Privacy | ✅ High | Homomorphic operations | Operator metadata access |
| Result Privacy | ✅ High | FHE ciphertext | Authorized decryption only |
| Input Validation | ⚠️ Medium | Abstracted ZKP oracle | Not cryptographic |
| Audit Integrity | ✅ High | Blockchain immutability | - |
| Availability | ❌ None | No DoS protection | - |
| Side-Channel Resistance | ❌ None | No hardening | - |

---

## 6. Mapping to Cryptographic Primitives

### 6.1 FHE (Fully Homomorphic Encryption)
- **Scheme**: CKKS (approximate) / BFV (exact)
- **Library**: Microsoft TenSEAL
- **Security Assumption**: Ring-LWE hardness
- **Parameters**: 
  - Polynomial modulus degree: 4096
  - Coefficient modulus: [40, 20, 40] bits (CKKS)
  - Security level: ~128 bits (estimated)

### 6.2 ZKP (Zero-Knowledge Proofs) - ABSTRACTED
- **Implementation**: Hash-based oracle simulation
- **NOT**: Cryptographic SNARK/STARK
- **Properties**: Simulates completeness and soundness
- **Zero-Knowledge**: Information-theoretic (abstracted)
- **Production Replacement**: Requires Circom/libsnark/Bulletproofs

### 6.3 Hash Functions
- **Algorithm**: SHA-256
- **Usage**: Input integrity, ZKP proof IDs
- **Security**: Collision resistance, pre-image resistance

---

## 7. Deployment Scenarios

### 7.1 Thesis Demonstration (Current Scope)
- **Environment**: Controlled local/testnet
- **Adversary Model**: Honest-but-curious
- **Acceptable**: Abstracted ZKP, trusted execution
- **Goal**: Concept validation, performance analysis

### 7.2 Production Deployment (Out of Scope)
- **Requirements**:
  - Replace abstracted ZKP with cryptographic implementation
  - Implement threshold FHE or secure key management
  - Add rate limiting and DoS protection
  - Formally verify smart contracts
  - Harden against side-channels
- **Security Level**: Byzantine fault tolerance
- **See**: `docs/limitations.md` for complete requirements

---

## 8. References

- **FHE Security**: Brakerski-Gentry-Vaikuntanathan (BGV) framework
- **CKKS**: Cheon-Kim-Kim-Song approximate arithmetic
- **ZKP Theory**: Goldwasser-Micali-Rackoff definitions  
- **Threat Modeling**: STRIDE framework adaptation

---

**Last Updated**: January 11, 2026  
**Document Status**: Academic thesis documentation  
**Intended Audience**: Thesis committee, security reviewers
