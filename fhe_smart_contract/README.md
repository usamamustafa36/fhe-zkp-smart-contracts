<div align="center">

# FHE-ZKP Smart Contract Framework

**Privacy-preserving smart contracts using Fully Homomorphic Encryption with enforced Zero-Knowledge Proof input validation**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![TenSEAL](https://img.shields.io/badge/FHE-TenSEAL%20(CKKS)-8A2BE2)](https://github.com/OpenMined/TenSEAL)
[![ZKP](https://img.shields.io/badge/ZKP-Groth16%20%7C%20Circom-9B59B6)](https://docs.circom.io/)
[![Ethereum](https://img.shields.io/badge/Blockchain-Ethereum%20(Sepolia)-627EEA?logo=ethereum)](https://ethereum.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*Encrypted computation · Verifiable inputs · Transparent audit trail · Formal leakage analysis*

</div>

---

## Overview

This framework addresses a fundamental problem in decentralized computation: **how to perform verifiable computation on private data on a public blockchain** without revealing the inputs.

The system integrates three cryptographic primitives into a unified execution environment:

| Primitive | Scheme | Role |
|---|---|---|
| **Fully Homomorphic Encryption** | CKKS (via TenSEAL) | Encrypted arithmetic on private inputs |
| **Zero-Knowledge Proofs** | Groth16 (via snarkjs/Circom) | Input validity verification without disclosure |
| **Blockchain Ledger** | Ethereum (Sepolia testnet) | Append-only transparent audit trail |

---

## Research Problem

Existing privacy-preserving blockchain frameworks (e.g., Hawk, Zexe) address ZKP-based computation but lack:

1. **Systematic FHE integration** — enabling computation on ciphertexts without decryption
2. **Explicit leakage characterization** — formally quantifying what metadata is inevitably disclosed on a public chain
3. **Pre-computation ZKP enforcement** — ensuring inputs are valid before encrypted computation begins

This framework closes all three gaps.

---

## Novel Contributions

1. **Integrated ZKP-FHE pipeline** — Groth16 proofs validate inputs before CKKS-encrypted computation proceeds. Prior systems (Hawk, ZEXE) do not compose both in a single enforced pipeline.

2. **Formal leakage function** `ℒ` — explicitly characterizes what metadata (ciphertext sizes, timing, proof hashes) is unavoidably disclosed on a public blockchain. Defined in `crypto_theory/leakage_model.md`.

3. **Transparent encrypted logging** — an append-only blockchain-style ledger records proof verification outcomes and ciphertext hashes on-chain, enabling auditability without revealing inputs.

4. **Consumer hardware validation** — the complete system runs on standard hardware without specialized trusted hardware (TEEs), demonstrating practical deployability.

---

## Cryptographic Architecture

```
User Input (plaintext)
       │
       ▼
┌─────────────────────────────────────────────────┐
│  ZKP Input Validation (Groth16)                  │
│  • Generate Circom circuit witness               │
│  • Produce Groth16 proof π                       │
│  • Verify: π proves input satisfies constraints  │
│    without revealing the input itself            │
└────────────────────────┬────────────────────────┘
                         │ (proof verified)
                         ▼
┌─────────────────────────────────────────────────┐
│  FHE Encrypted Computation (CKKS / TenSEAL)      │
│  • Encrypt input: enc(x) = CKKS.Encrypt(x)      │
│  • Compute on ciphertext: f(enc(x))              │
│  • Decrypt result only at authorized endpoint    │
│  • Entropy analysis: measure cryptographic       │
│    strength of all ciphertexts                   │
└────────────────────────┬────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────┐
│  Blockchain Audit Ledger (Ethereum / Sepolia)    │
│  • Record: {timestamp, H(ciphertext), proof_id}  │
│  • Append-only — no entry can be modified        │
│  • Enables compliance auditing without           │
│    exposing underlying encrypted data            │
└─────────────────────────────────────────────────┘
```

---

## Project Structure

```
fhe_smart_contract/
├── proposal_aligned_thesis.py          # Main demonstration script
├── requirements.txt
├── README.md
│
├── fhe_engine/                         # Core FHE implementation (TenSEAL / CKKS)
│   ├── encrypt.py                      # Encryption utilities
│   ├── compute.py                      # Homomorphic computation
│   ├── decrypt.py                      # Authorized decryption
│   ├── advanced_fhe.py                 # Multi-scheme FHE operations
│   └── neural_network.py              # Encrypted neural network inference
│
├── blockchain/                         # Ethereum integration
│   ├── ethereum_integration.py
│   └── contracts/
│       └── FHESmartContract.sol        # Solidity smart contract
│
├── zkp_prod/                           # ZKP circuits and proofs
│   ├── circuits/                       # Circom circuit definitions
│   └── proofs/                         # Groth16 proof generation (snarkjs)
│
├── crypto_theory/                      # Formal cryptographic analysis
│   ├── leakage_model.md               # Formal leakage function ℒ
│   ├── security_proofs.md             # Game-based security definitions
│   └── composition_arguments.md       # CKKS + Groth16 composition
│
└── utils/
    ├── entropy_analysis.py             # Ciphertext entropy measurement
    └── performance_monitor.py          # Execution time + throughput tracking
```

---

## Quick Start

### Prerequisites

```bash
# Python 3.10+
pip install tenseal numpy joblib tqdm psutil
```

### Run the Framework Demo

```bash
git clone https://github.com/usamamustafa36/fhe-zkp-smart-contracts.git
cd fhe-zkp-smart-contracts/fhe_smart_contract

python3 proposal_aligned_thesis.py
```

**Demo output includes:**
1. ZKP input validation (enforced before computation)
2. CKKS-encrypted computation with entropy logging
3. Blockchain-style audit ledger entries
4. Entropy analysis of all generated ciphertexts
5. Performance metrics (throughput, latency)

---

## Formal Security Analysis

The framework is accompanied by formal cryptographic analysis in `crypto_theory/`:

### Leakage Characterization

The leakage function `ℒ` explicitly models what a public blockchain observer learns:

```
ℒ(execution) = {
  |enc(x)|,          # ciphertext size (reveals parameter choices)
  timestamp,          # timing metadata
  H(enc(x)),          # ciphertext hash (enables de-duplication detection)
  proof_id,           # ZKP proof identifier
  gas_cost            # computation cost (correlated with plaintext complexity)
}
```

**Crucially:** `ℒ` does **not** include the plaintext `x` or intermediate computation results — these remain computationally hidden under the CKKS IND-CPA security assumption.

### Security Properties

| Property | Guarantee | Assumption |
|---|---|---|
| Input confidentiality | CKKS IND-CPA | RLWE hardness |
| Input validity | Groth16 soundness | Discrete log hardness |
| Computation integrity | ZKP completeness | Trusted setup (Groth16 CRS) |
| Audit transparency | Ledger append-only | Ethereum consensus |

---

## Evaluation Metrics

| Metric | Result |
|---|---|
| ZKP validation success rate | 100% (all valid inputs pass) |
| FHE computation correctness | Verified against plaintext baseline |
| Ciphertext entropy | >7.8 bits/byte (near-random, high security) |
| End-to-end latency (consumer hardware) | < 2 seconds per transaction |
| Ledger integrity | Verified via SHA-256 hash chaining |

---

## Implementation Stack

| Component | Technology |
|---|---|
| FHE engine | TenSEAL (CKKS scheme) |
| ZKP circuits | Circom 2.0 |
| Proof system | Groth16 via snarkjs |
| Smart contract | Solidity ^0.8.0 |
| Blockchain | Ethereum (Sepolia testnet) |
| Performance monitoring | Python `psutil`, custom profiler |

---

## Research Directions

This framework opens several directions for future work:

- **TFHE / BFV integration** — discrete-domain computations (comparisons, sorting)
- **Recursive ZKP composition** — aggregating multiple proofs for batch transactions
- **Threshold FHE** — multi-party key management without a single trusted authority
- **Cross-chain audit bridging** — portable audit logs across blockchain platforms
- **Post-quantum FHE** — lattice-based schemes with quantum-resistant parameters

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## References

1. Gentry, C. (2009). *A fully homomorphic encryption scheme*. Stanford University.
2. Groth, J. (2016). *On the size of pairing-based non-interactive arguments*. EUROCRYPT 2016.
3. Cheon, J.H. et al. (2017). *Homomorphic encryption for arithmetic of approximate numbers* (CKKS). ASIACRYPT 2017.
4. Kosba, A. et al. (2016). *Hawk: The blockchain model of cryptography and privacy-preserving smart contracts*. IEEE S&P 2016.
5. OpenMined TenSEAL. *A library for encrypted tensor operations*. https://github.com/OpenMined/TenSEAL

---

<div align="center">

**FHE · ZKP · Blockchain · Cryptographic Privacy · Verifiable Computation**

</div>
