# Mathematical Notation Reference

**Purpose:** Standard cryptographic notation used throughout `crypto_theory/` analysis.

---

## General Notation

| Symbol | Meaning |
|--------|---------|
| λ | Security parameter (e.g., λ = 128 bits) |
| negl(λ) | Negligible function in λ (vanishes faster than any polynomial) |
| poly(λ) | Polynomial function in λ |
| x ← S | Sample x uniformly from set S |
| x ← A(y) | x is output of algorithm A on input y |
| [n] | The set {1, 2, ..., n} |
| ⊥ | Error symbol / rejection |
| ∥ | Concatenation |
| ⊕ | XOR / addition in ℤ₂ |

---

## Cryptographic Primitives

### FHE (Fully Homomorphic Encryption)

**Scheme:** Π_FHE = (KeyGen, Enc, Dec, Eval)

| Algorithm | Notation | Description |
|-----------|----------|-------------|
| Key Generation | (pk, sk) ← KeyGen(1^λ) | Generate public/secret key pair |
| Encryption | ct ← Enc(pk, m) | Encrypt message m under pk |
| Decryption | m' ← Dec(sk, ct) | Decrypt ciphertext ct using sk |
| Evaluation | ct_f ← Eval(pk, f, ct₁, ..., ctₙ) | Homomorphically evaluate function f |

**Message Space:** ℳ (e.g., ℂᵈ for CKKS with dimension d)  
**Ciphertext Space:** 𝒞  
**Function Space:** ℱ (arithmetic circuits over ℳ)

### ZKP (Zero-Knowledge Proof)

**Scheme:** Π_ZKP = (Setup, Prove, Verify)

| Algorithm | Notation | Description |
|-----------|----------|-------------|
| Setup | (ek, vk) ← Setup(1^λ, ℛ) | Generate proving/verification keys for relation ℛ |
| Prove | π ← Prove(ek, x, w) | Generate proof π that (x, w) ∈ ℛ |
| Verify | {0, 1} ← Verify(vk, x, π) | Verify proof π for statement x |

**Relation:** ℛ = {(x, w) : φ(x, w) = 1} where x is public, w is witness  
**Statement:** x ∈ {0, 1}*  
**Witness:** w ∈ {0, 1}*

---

## System-Specific Notation

### Blockchain Context

| Symbol | Meaning |
|--------|---------|
| 𝔹 | Blockchain state |
| tx | Transaction |
| addr | Ethereum address (20 bytes) |
| chainID | Chain identifier (uint256) |
| gasUsed | Gas consumed by transaction |
| T | Timestamp |

### Our Protocol

| Symbol | Meaning |
|--------|---------|
| x | Private input value (plaintext) |
| m | Message vector for CKKS encryption |
| ct | Ciphertext (FHE encrypted value) |
| π | Zero-knowledge proof |
| σ | Salt (random value for commitment) |
| H | Commitment hash |
| C | Context binding value |
| 𝒪 | Off-chain operator |
| 𝒰 | User (client) |
| 𝒜 | Adversary |

---

## Security Definitions

### Advantage Functions

**IND-CPA advantage of adversary 𝒜:**
```
Adv^{ind-cpa}_{Π_FHE,𝒜}(λ) = |Pr[𝒜 wins IND-CPA game] - 1/2|
```

**ZK soundness error of adversary 𝒜:**
```
ε_{sound}(λ) = Pr[𝒜 produces accepting proof for false statement]
```

**ZK knowledge error:**
```
ε_{know}(λ) = Pr[𝒜 produces proof without witness w]
```

### Negligibility

A function f(λ) is **negligible**, written f(λ) ∈ negl(λ), if:
```
∀c > 0, ∃λ₀, ∀λ > λ₀ : f(λ) < 1/λᶜ
```

### Computational Indistinguishability

Two distributions D₀, D₁ are **computationally indistinguishable**, written D₀ ≈_c D₁, if:
```
∀ PPT adversary 𝒜 : |Pr[𝒜(D₀) = 1] - Pr[𝒜(D₁) = 1]| ∈ negl(λ)
```

---

## Probability Notation

| Symbol | Meaning |
|--------|---------|
| Pr[E] | Probability of event E |
| 𝔼[X] | Expected value of random variable X |
| Pr[E₁ ∧ E₂] | Probability of E₁ AND E₂ |
| Pr[E₁ \| E₂] | Conditional probability of E₁ given E₂ |

---

## Error and Noise

**CKKS-specific:**

| Symbol | Meaning |
|--------|---------|
| ε | Approximation error bound |
| Δ | Scaling factor |
| B_noise | Noise bound |
| q | Ciphertext modulus |
| L | Multiplicative depth |
| N | RLWE dimension |

**Error growth:**
```
‖noise(ct_f)‖ ≤ poly(L, N) · B_noise
```

---

## Complexity Classes

| Class | Description |
|-------|-------------|
| PPT | Probabilistic Polynomial Time |
| NP | Nondeterministic Polynomial time |
| co-NP | Complement of NP |
| BPP | Bounded-error Probabilistic Polynomial time |

---

## Cryptographic Assumptions

### RLWE (Ring Learning With Errors)

**Assumption:** For polynomial ring R = ℤ[X]/(Φ_N(X)), modulus q, error distribution χ:

```
(a, b = a·s + e) ≈_c (a, u)
```

where a ←$ R_q, s, e ← χ, u ←$ R_q

**Security Level:** λ bits (e.g., λ = 128 for parameters N = 2^14, log q = 438)

### Pairing Hardness (for Groth16)

**Bilinear Groups:** (𝔾₁, 𝔾₂, 𝔾_T, e, p, g₁, g₂) where e: 𝔾₁ × 𝔾₂ → 𝔾_T

**q-SDH Assumption:** Given (g, g^x, g^{x²}, ..., g^{x^q}), hard to compute (c, g^{1/(x+c)})

**q-PKE Assumption:** Decisional assumption for pairing-based knowledge extraction

---

## Function Notation

### Homomorphic Operations

**Addition:**
```
ct₁ ⊞ ct₂ := Eval(pk, +, ct₁, ct₂)
```

**Multiplication:**
```
ct₁ ⊠ ct₂ := Eval(pk, ×, ct₁, ct₂)
```

**Scalar multiplication:**
```
α ⊙ ct := Eval(pk, (λx. α·x), ct)
```

### Leakage Function

```
ℒ : Protocol_State → {0,1}*
```

Maps protocol execution state to publicly observable information.

---

## Cryptographic Games

### IND-CPA Game for FHE

```
Game IND-CPA^{𝒜}_{Π_FHE}(λ):
    (pk, sk) ← KeyGen(1^λ)
    (m₀, m₁, state) ← 𝒜₁(pk)
    b ←$ {0, 1}
    ct* ← Enc(pk, m_b)
    b' ← 𝒜₂(ct*, state)
    return (b = b')
```

### ZK Soundness Game

```
Game Soundness^{𝒜}_{Π_ZKP}(λ, ℛ):
    (ek, vk) ← Setup(1^λ, ℛ)
    (x, π) ← 𝒜(ek, vk)
    if Verify(vk, x, π) = 1 and ∀w : (x, w) ∉ ℛ:
        return 1  // 𝒜 wins
    return 0
```

---

## Reduction Notation

**Reduction from Problem A to Problem B:**
```
𝒜 (breaks B) ⟹ ℬ (breaks A)
```

Written as:
```
Adv^A_ℬ ≥ Adv^B_𝒜 - negl(λ)
```

Interpretation: If B is hard, then A is hard.

---

## Asymptotic Notation

| Notation | Meaning |
|----------|---------|
| O(f(n)) | Upper bound (≤ c·f(n) for some c) |
| Ω(f(n)) | Lower bound (≥ c·f(n) for some c) |
| Θ(f(n)) | Tight bound (both O and Ω) |
| õ(f(n)) | Soft-O (ignoring log factors) |

---

## References

Standard notation follows:

1. **Goldreich, O.** "Foundations of Cryptography: Basic Tools" (2001)
2. **Katz, J. & Lindell, Y.** "Introduction to Modern Cryptography" (2014)
3. **Boneh, D. & Shoup, V.** "A Graduate Course in Applied Cryptography" (2020)

CKKS-specific notation from:

4. **Cheon et al.** "Homomorphic Encryption for Arithmetic of Approximate Numbers" (ASIACRYPT 2017)

Groth16-specific notation from:

5. **Groth, J.** "On the Size of Pairing-based Non-interactive Arguments" (EUROCRYPT 2016)
