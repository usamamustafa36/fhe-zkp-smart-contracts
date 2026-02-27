# Formal Security Model

**Purpose:** Precise cryptographic definitions for FHE + ZKP composition in blockchain context.

**Notation:** See `notation.md` for symbol definitions.

---

## 1. System Model

### 1.1 Participants

**Definition 1.1 (System Participants)**

The system comprises the following polynomial-time entities:

1. **User 𝒰 = (𝒰_KeyGen, 𝒰_Encrypt, 𝒰_Prove, 𝒰_Decrypt)**
   - Generates FHE keys: (pk_FHE, sk_FHE) ← 𝒰_KeyGen(1^λ)
   - Encrypts inputs: ct ← 𝒰_Encrypt(pk_FHE, x)
   - Generates ZK proofs: π ← 𝒰_Prove(ek_ZKP, x, σ)
   - Decrypts outputs: y ← 𝒰_Decrypt(sk_FHE, ct_result)

2. **Off-Chain Operator 𝒪 = (𝒪_Compute, 𝒪_Submit)**
   - Performs FHE computation: ct_result ← 𝒪_Compute(pk_FHE, f, ct)
   - Submits to blockchain: tx ← 𝒪_Submit(ct_result, metadata)
   - **Trust Model:** Honest-but-curious (executes correctly, may observe)

3. **Blockchain 𝔹 = (𝔹_Store, 𝔹_Verify)**
   - Stores transactions: state' ← 𝔹_Store(state, tx)
   - Verifies ZK proofs: {0, 1} ← 𝔹_Verify(vk_ZKP, π, public_inputs)
   - **Properties:** Public, immutable, ordered log

4. **Adversary 𝒜 = (𝒜₁, 𝒜₂)**
   - Type I: Honest-but-curious (passive observation)
   - Type II: Malicious (active manipulation)
   - **Constraints:** Polynomial-time (PPT), cannot break cryptographic assumptions

### 1.2 Cryptographic Primitives

**Definition 1.2 (FHE Scheme)**

An FHE scheme Π_FHE = (KeyGen, Enc, Dec, Eval) over message space ℳ and function space ℱ consists of:

- **KeyGen(1^λ) → (pk, sk):** Generate public/secret keys
- **Enc(pk, m ∈ ℳ) → ct:** Encrypt message
- **Dec(sk, ct) → m' ∈ ℳ ∪ {⊥}:** Decrypt ciphertext
- **Eval(pk, f ∈ ℱ, ct₁, ..., ctₙ) → ct_f:** Homomorphic evaluation

**Correctness:** For all λ ∈ ℕ, m₁, ..., mₙ ∈ ℳ, f ∈ ℱ:
```
Pr[Dec(sk, Eval(pk, f, Enc(pk, m₁), ..., Enc(pk, mₙ))) = f(m₁, ..., mₙ)] ≥ 1 - negl(λ)
```

**For CKKS:** This is approximate correctness with error ε (see Section 4).

**Definition 1.3 (ZKP Scheme)**

A non-interactive zero-knowledge proof (NIZK) scheme Π_ZKP = (Setup, Prove, Verify) for NP relation ℛ consists of:

- **Setup(1^λ, ℛ) → (ek, vk):** Generate evaluation/verification keys
- **Prove(ek, x, w) → π:** Generate proof for (x, w) ∈ ℛ
- **Verify(vk, x, π) → {0, 1}:** Verify proof

**Properties:** (Completeness, Soundness, Zero-Knowledge) - See Section 2.3.

### 1.3 System Parameters

**Public Parameters pp:**
- Security parameter: λ = 128
- FHE parameters: N = 2^13 = 8192 (RLWE dimension), log q ≈ 200 (modulus chain [60,40,40,60])
- ZKP curve: BN254 (pairing-friendly)
- Blockchain: chainID (e.g., 11155111 for Sepolia)
- Range bound: R = 1,000,000 (input validation range)

**Note on Parameter Selection:**
The implementation uses N = 8192 with coefficient modulus chain [60, 40, 40, 60]
(log q ≈ 200 bits), achieving ≥ 128-bit security under the RLWE hardness
assumption at this dimension (consistent with NIST/Homomorphic Encryption Standard
recommendations for λ = 128 at N = 8192 and log q ≤ 218).

Performance benchmarks in Chapter 8 were conducted with the same secure parameters.
A reduced parameter set (N = 4096, [40, 20, 40], λ ≈ 80 bits) is also available
as `AdvancedFHE.BENCHMARK_PARAMS` for timing micro-benchmarks only, and is
**not** intended for security-sensitive deployment.

**Keys:**
- FHE keys: (pk_FHE, sk_FHE) held by user 𝒰
- ZKP keys: (ek_ZKP, vk_ZKP) generated in trusted setup, vk_ZKP public on 𝔹

---

## 2. Protocol Specification

### 2.1 Input Validation Protocol Π_IV

**Input:** Private value x ∈ [0, R], context C = (chainID, addr, opType, reqID)

**Phase 1: Client-Side Proof Generation**
```
1. Sample salt σ ←$ {0,1}^256
2. Compute context hash: h_C ← H(C)
3. Compute commitment: H ← Poseidon(x, σ, h_C)
4. Generate proof: π ← Prove(ek_ZKP, (H, h_C), (x, σ))
5. Output: (π, H, h_C)
```

**Phase 2: On-Chain Verification**
```
1. Parse public inputs: (H, h_C)
2. Verify proof: b ← Verify(vk_ZKP, (H, h_C), π)
3. Verify context: h_C = H(C) where C includes current chainID, msg.sender
4. Check anti-replay: reqID not previously used
5. If all checks pass: store (H, h_C, π) on blockchain
6. Else: revert transaction
```

**Relation ℛ_Range:**
```
ℛ_Range = {((H, h_C), (x, σ)) : 
    0 ≤ x ≤ R ∧ H = Poseidon(x, σ, h_C)}
```

### 2.2 FHE Computation Protocol Π_FC

**Input:** Ciphertext ct = Enc(pk_FHE, x), function f ∈ ℱ

**Phase 1: Off-Chain Computation**
```
1. Operator 𝒪 receives ct from user 𝒰
2. Compute: ct_result ← Eval(pk_FHE, f, ct)
3. Output: ct_result
```

**Phase 2: Result Submission**
```
1. 𝒪 submits tx = (ct_result, metadata) to 𝔹
2. 𝔹 stores tx in immutable log
3. User 𝒰 retrieves ct_result, computes y ← Dec(sk_FHE, ct_result)
```

### 2.3 Composed Protocol Π = Π_IV ∘ Π_FC

**Full Protocol Execution:**

```
Protocol Π(x, f, C):
    // Client side
    (pk_FHE, sk_FHE) ← KeyGen(1^λ)
    ct ← Enc(pk_FHE, x)
    (π, H, h_C) ← Π_IV(x, C)
    
    // Blockchain verification
    if Verify(vk_ZKP, (H, h_C), π) = 0:
        return ⊥
    
    // Off-chain computation
    ct_result ← Π_FC(ct, f)
    
    // Result retrieval
    y ← Dec(sk_FHE, ct_result)
    return y
```

---

## 3. Adversary Model

### 3.1 Adversarial Capabilities

**Definition 3.1 (Honest-but-Curious Adversary 𝒜_HBC)**

An adversary 𝒜_HBC is PPT and has the following capabilities:

1. **Observation:** Can observe all blockchain transactions 𝔹
2. **Operator Role:** Can play role of 𝒪 (sees ciphertexts, performs computation)
3. **Passive:** Follows protocol correctly, but tries to learn x

**Restrictions:**
- Cannot break FHE (RLWE assumption holds)
- Cannot break ZKP soundness (pairing assumptions hold)
- Cannot obtain sk_FHE (key security)

**Goal:** Learn information about x beyond what is leaked by ℒ (see leakage_model.md)

**Definition 3.2 (Malicious Adversary 𝒜_MAL)**

An adversary 𝒜_MAL is PPT and has the following capabilities:

1. **All 𝒜_HBC capabilities** (observation, operator role)
2. **Deviation:** Can deviate from protocol arbitrarily
3. **Forgery Attempts:** Can submit arbitrary transactions to 𝔹

**Restrictions:**
- Cannot break cryptographic assumptions (PPT bounded)
- Cannot compromise sk_FHE (out of scope)
- Cannot break blockchain consensus (separate concern)

**Goal:** 
- Learn x (confidentiality attack)
- Cause acceptance of invalid x ∉ [0, R] (soundness attack)
- Replay old proofs (anti-replay attack)
- Manipulate computation result (correctness attack)

### 3.2 Adversarial Limitations

**Out of Scope:**
1. Side-channel attacks (timing, power, cache)
2. Trusted setup compromise (toxic waste)
3. Blockchain consensus attacks (51%, selfish mining)
4. Social engineering (phishing for sk_FHE)
5. Quantum adversaries (requires PQ-secure schemes)

---

## 4. Security Goals

### 4.1 Confidentiality

**Definition 4.1 (Computational Input Privacy)**

Protocol Π provides computational input privacy if for all PPT adversaries 𝒜 = (𝒜₁, 𝒜₂):

```
Game InputPrivacy^𝒜_Π(λ):
    pp ← Setup(1^λ)
    (x₀, x₁, state) ← 𝒜₁(pp)
    b ←$ {0, 1}
    transcript ← Execute_Π(x_b)
    b' ← 𝒜₂(transcript, state)
    return (b = b')

Adv^{priv}_Π,𝒜(λ) := |Pr[Game outputs 1] - 1/2| ∈ negl(λ)
```

**Interpretation:** Adversary cannot distinguish protocol executions for different inputs x₀, x₁, even when observing full blockchain transcript and acting as operator.

**Caveat:** Leakage via ℒ is unavoidable (ciphertext size, gas, timing). Privacy holds for information beyond ℒ.

### 4.2 Soundness (Input Validation)

**Definition 4.2 (Computational Soundness)**

Protocol Π provides computational soundness if for all PPT adversaries 𝒜:

```
Game Soundness^𝒜_Π(λ):
    pp ← Setup(1^λ)
    (π, H, h_C) ← 𝒜(pp)
    if Verify(vk_ZKP, (H, h_C), π) = 1:
        Extract (x, σ) from 𝒜 via knowledge extractor
        if x ∉ [0, R]:
            return 1  // 𝒜 wins
    return 0

Pr[Game outputs 1] ∈ negl(λ)
```

**Interpretation:** Adversary cannot produce an accepting proof for an invalid input x ∉ [0, R].

**Knowledge Extraction:** By knowledge soundness of Groth16, if 𝒜 produces accepting π, then 𝒜 "knows" witness (x, σ) such that relation holds.

### 4.3 Correctness

**Definition 4.3 (Approximate Computational Correctness)**

Protocol Π provides ε-approximate correctness if for all x ∈ ℳ, f ∈ ℱ with depth ≤ L:

```
Pr[|Π(x, f) - f(x)| > ε] ∈ negl(λ)
```

where probability is over randomness of KeyGen, Enc, Eval.

**For CKKS:** Error ε = O(2^(-p)) where p is precision bits (see correctness_theorem.md).

**Caveat:** 
- Operator 𝒪 is trusted to compute correctly
- FHE noise must remain bounded (depth L constraints)
- Approximate (not perfect) for CKKS

### 4.4 Anti-Replay Protection

**Definition 4.4 (Request Uniqueness)**

Protocol Π provides anti-replay protection if:

```
∀ valid proof (π, H, h_C) with context C = (chainID, addr, opType, reqID):
    If blockchain 𝔹 has accepted (π, H, h_C) for reqID,
    then 𝔹 rejects all future submissions with same reqID
```

**Mechanism:** Context binding via h_C = H(chainID, addr, opType, reqID) where reqID is unique (e.g., timestamp-based).

---

## 5. Cryptographic Assumptions

### 5.1 RLWE Assumption (FHE Security)

**Assumption 5.1 (Ring-LWE)**

For security parameter λ, polynomial degree N, modulus q, error distribution χ over ring R = ℤ[X]/(X^N + 1):

```
{(a, a·s + e) : a ←$ R_q, s, e ← χ} ≈_c {(a, u) : a, u ←$ R_q}
```

**Standard Parameters for λ = 128:**
- N = 2^14 = 16384
- log q ≈ 438
- χ = discrete Gaussian with σ = 3.2

**Security:** Believed to be post-quantum secure (reduction to worst-case lattice problems).

### 5.2 Pairing Assumptions (Groth16 Security)

**Assumption 5.2 (q-Power Knowledge of Exponent - q-PKE)**

For bilinear groups (𝔾₁, 𝔾₂, 𝔾_T, e), adversary 𝒜 who produces group elements must "know" discrete logarithms.

**Implication:** Knowledge soundness for Groth16 SNARKs.

**Assumption 5.3 (q-Strong Diffie-Hellman - q-SDH)**

Given (g, g^x, g^{x²}, ..., g^{x^q}), it is hard to compute (c, g^{1/(x+c)}) for c ≠ 0.

**Implication:** Computational soundness for Groth16.

**Security Level:** λ = 128 bits for BN254 curve at 2017 security estimates.

**Note:** Pairing-based assumptions are **not** post-quantum secure.

### 5.3 Commitment Binding

**Assumption 5.4 (Poseidon Collision Resistance)**

For hash function Poseidon: {0,1}* → 𝔽_p:

```
Pr[(x, σ, h) ≠ (x', σ', h') ∧ Poseidon(x, σ, h) = Poseidon(x', σ', h')] ∈ negl(λ)
```

**Justification:** Poseidon designed for algebraic hash with sponge construction, security reduction to permutation security.

---

## 6. Security Model Summary

### 6.1 What We Model

✅ **Computational adversaries** (PPT, cannot break assumptions)  
✅ **Passive observation** (honest-but-curious operator)  
✅ **Active attacks** (malicious proof submission, replay)  
✅ **Blockchain public execution** (full transcript visible)  
✅ **Approximate correctness** (CKKS error bounds)

### 6.2 What We Do Not Model

❌ **Side channels** (standard model only)  
❌ **Quantum adversaries** (Groth16 not PQ-secure)  
❌ **Trusted setup compromise** (toxic waste vulnerability)  
❌ **Verifiable computation** (operator correctness not proven)  
❌ **Byzantine blockchain** (consensus-level attacks)

### 6.3 Relationship to Practice

**Theory → Implementation:**
- FHE scheme Π_FHE → TenSEAL (CKKS) in `core/fhe_engine.py`
- ZKP scheme Π_ZKP → Groth16 (Circom) in `zkp_prod/`
- Adversary 𝒜_HBC → Blockchain observer (any node)
- Adversary 𝒜_MAL → Malicious transaction submitter

**Implementation → Evaluation:**
- Correctness (Def 4.3) → Validated in `crypto/correctness.py`
- Leakage ℒ → Measured in `evaluation/cost_analysis.py`
- Performance → Benchmarked in `evaluation/performance.py`

---

## 7. References

### Formal Methods
1. **Bellare, M. & Rogaway, P.** "The Security of Triple Encryption and a Framework for Code-Based Game-Playing Proofs." EUROCRYPT 2006.
2. **Goldwasser, S. & Micali, S.** "Probabilistic Encryption." JCSS 1984.

### FHE Security Models
3. **Gentry, C.** "Fully Homomorphic Encryption Using Ideal Lattices." STOC 2009.
4. **Brakerski, Z. & Vaikuntanathan, V.** "Efficient Fully Homomorphic Encryption from (Standard) LWE." FOCS 2011.

### ZKP Security Models
5. **Goldreich, O., Micali, S., Wigderson, A.** "Proofs that Yield Nothing But Their Validity." JACM 1991.
6. **Groth, J.** "On the Size of Pairing-based Non-interactive Arguments." EUROCRYPT 2016.

### Composition
7. **Canetti, R.** "Universally Composable Security." JACM 2001.
8. **Goldreich, O.** "Foundations of Cryptography: Volume 2." Cambridge University Press, 2004.

---

**Next:** See `composition_analysis.md` for security reduction arguments.
