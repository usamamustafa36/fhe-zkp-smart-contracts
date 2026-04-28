# Circuit Specification

## 🎯 Purpose
The `range_commit` circuit validates that a secret value `x` is within the allowed range while binding it to a specific execution context to prevent replay attacks.

## 🧩 Structure

### Inputs
- **Private**:
  - `x`: The secret value (must be 0-1,000,000).
  - `salt`: Random salt for commitment hiding.
- **Public**:
  - `commitment`: Poseidon(x, salt, contextHash).
  - `contextHash`: Poseidon(chainId, contractAddr, opType, requestId).

### Constraints
1. **Range Proof**:
   - Uses `LessEqThan(32)` to prove `x <= 1,000,000`.
   - `x >= 0` is implicit in the field arithmetic for small values.
2. **Binding**:
   - `Poseidon(x, salt, contextHash) === commitment`.

## 🔒 Security Properties

### Completeness
Any valid `x` in range will produce a valid proof.

### Soundness
No adversary can produce a valid proof for `x > 1,000,000` assuming the difficulty of the discrete log problem on BN254.

### Zero-Knowledge
The proof reveals no information about `x` other than it satisfies the constraints.

### Binding
The proof is cryptographically bound to the `contextHash`. Reusing the proof on a different chain or contract will fail as the public signals won't match.

## 🛠️ Implementation Details
- **Compiler**: Circom 2.1.6+
- **Protocol**: Groth16
- **Curve**: BN128 (BN254)
- **Library**: `circomlib` (Poseidon, Comparators)
