# ZKP Operations Guide

This document explains how to generate and verify proofs in production.

## 🛠️ Proof Generation (Python)

The primary interface for proof generation is `ProductionZKPProver`.

### Example
```python
from zkp_prod.python.zkp_prover import ProductionZKPProver

prover = ProductionZKPProver()

# Generate proof
proof = prover.generate_proof(
    x=500000,
    chain_id=11155111,
    contract_address=b'\x01'*20,
    operation_type=0,
    request_id=b'\x02'*32
)
```

## 🛡️ Witness Protection

The prover implements several security features:
1. **Sanitization**: Private inputs are never logged.
2. **Ephemeral Files**: Witness files are created in `/tmp` and deleted immediately after proof generation.
3. **Entropy**: Salts are generated using cryptographically secure RNG.

## ✅ On-Chain Verification

The `Verifier.sol` contract is generated during the build process.

### Integration
1. Deploy `Verifier.sol`.
2. Call `verifyProof(a, b, c, [commitment, contextHash])`.
3. The `contextHash` must be computed as:
   `Poseidon(chainId, contractAddr, opType, requestId)`

## 🔍 Troubleshooting

### Include errors during build:
Ensure you are using `circom ... -l zkp_prod/node_modules`.

### Proof verification fails:
1. Ensure `x` is strictly within [0, 1,000,000].
2. Ensure `contextHash` matches exactly between Python and Solidity.
3. Verify `Verifier.sol` matches the `zkey` used in proof generation.
