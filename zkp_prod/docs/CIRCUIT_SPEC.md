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
   - `Num2Bits(32)` constrains `x` to 32 bits, so `0 <= x < 2^32`. This is required: `LessEqThan(n)` is only sound for inputs already known to fit in n bits, and without it a field element such as `p - 1` ("-1") passes the check.
   - `LessEqThan(32)` then proves `x <= 1,000,000`.
   - Regression test: `zkp_prod/tests/circuit/test_range_soundness.sh`.
2. **Binding**:
   - `Poseidon(x, salt, contextHash) === commitment`.

## 🔒 Security Properties

### Completeness
Any valid `x` in range will produce a valid proof.

### Soundness
No adversary can produce a valid proof for `x` outside [0, 1,000,000], assuming the Groth16 knowledge-soundness assumptions (generic/algebraic group model on BN254) and an honest trusted setup. (Discrete-log hardness alone is not sufficient for Groth16 soundness.)

### Zero-Knowledge
The proof reveals no information about `x` other than it satisfies the constraints.

### Binding
The proof is cryptographically bound to the `contextHash`. Reusing the proof on a different chain or contract will fail as the public signals won't match.

## 🛠️ Implementation Details
- **Compiler**: Circom 2.1.6+
- **Protocol**: Groth16
- **Curve**: BN128 (BN254)
- **Library**: `circomlib` (Poseidon, Comparators)
