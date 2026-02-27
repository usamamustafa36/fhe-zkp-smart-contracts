# Composition Security Analysis

**Purpose:** Reduction-based argument for FHE + ZKP composed protocol security.

**Prerequisites:** Read `security_model.md` for definitions and notation.

---

## 1. Overview

### 1.1 Composition Challenge

We compose two cryptographic primitives:
- **CKKS FHE (Π_FHE):** Provides computational privacy (IND-CPA)
- **Groth16 NIZK (Π_ZKP):** Provides soundness and zero-knowledge

**Question:** Does composition Π = Π_IV ∘ Π_FC preserve security properties?

**Answer:** Yes, under standard assumptions, with explicit leakage ℒ.

### 1.2 Main Result (Informal)

**Theorem 1.1 (Composition Security - Informal)**

If Π_FHE is IND-CPA secure and Π_ZKP is a zero-knowledge argument of knowledge, then composed protocol Π provides:

1. **Input Privacy:** Against honest-but-curious adversaries
2. **Soundness:** Against malicious adversaries submitting invalid proofs  
3. **Anti-Replay:** Against malicious adversaries reusing proofs

**Caveat:** Leakage function ℒ reveals:
- Ciphertext sizes (≈ 6KB per CKKS ciphertext)
- Gas consumption (≈ 90K-110K gas per proof verification)
- Transaction timing and sender addresses

Privacy holds for information beyond ℒ.

---

## 2. Input Privacy Analysis

### 2.1 Privacy Against Passive Adversaries

**Theorem 2.1 (Input Privacy)**

Let Π_FHE be an IND-CPA secure FHE scheme and Π_ZKP be a zero-knowledge NIZK. Then composed protocol Π provides computational input privacy as defined in Definition 4.1 (security_model.md).

Formally, for any PPT adversary 𝒜 = (𝒜₁, 𝒜₂) attacking input privacy:

```
Adv^{priv}_Π,𝒜(λ) ≤ Adv^{ind-cpa}_{Π_FHE,ℬ₁}(λ) + Adv^{zk}_{Π_ZKP,ℬ₂}(λ) + negl(λ)
```

where ℬ₁, ℬ₂ are PPT adversaries constructed from 𝒜.

### 2.2 Proof Sketch

**Game Sequence:**

**Game 0 (Real Protocol):** 
- Challenge bit b ←$ {0,1}
- User encrypts: ct ← Enc(pk_FHE, x_b)
- User proves: π ← Prove(ek_ZKP, (H_b, h_C), (x_b, σ))
- Operator computes: ct_result ← Eval(pk_FHE, f, ct)
- Adversary 𝒜 sees: (ct, π, H_b, h_C, ct_result)
- Output: b' ← 𝒜(view)

**Game 1 (Simulated Proof):**
- Replace real proof π with simulated proof π_sim ← Sim(vk_ZKP, (H_b, h_C))
- By zero-knowledge property of Π_ZKP:
  ```
  |Pr[𝒜 wins Game 0] - Pr[𝒜 wins Game 1]| ≤ Adv^{zk}_{Π_ZKP,ℬ₂}(λ)
  ```
- **Reduction ℬ₂:** If 𝒜 distinguishes games, ℬ₂ breaks ZK property

**Game 2 (Random Ciphertext):**
- Replace ct ← Enc(pk_FHE, x_b) with ct ←$ 𝒞 (uniform random ciphertext)
- By IND-CPA security of Π_FHE:
  ```
  |Pr[𝒜 wins Game 1] - Pr[𝒜 wins Game 2]| ≤ Adv^{ind-cpa}_{Π_FHE,ℬ₁}(λ)
  ```
- **Reduction ℬ₁:** If 𝒜 distinguishes games, ℬ₁ breaks FHE IND-CPA

**Game 3 (Random Everything):**
- ct_result ← Eval(pk_FHE, f, ct) where ct is random
- By FHE correctness, this is computationally independent of x_b
- Adversary advantage negligible: Pr[𝒜 wins Game 2] - 1/2 ∈ negl(λ)

**Combining Games:**
```
Adv^{priv}_Π,𝒜(λ) = |Pr[Game 0 outputs 1] - 1/2|
                  ≤ |Pr[Game 0] - Pr[Game 1]| + |Pr[Game 1] - Pr[Game 2]| + |Pr[Game 2] - 1/2|
                  ≤ Adv^{zk}_{Π_ZKP,ℬ₂}(λ) + Adv^{ind-cpa}_{Π_FHE,ℬ₁}(λ) + negl(λ)
```

Both advantages are negligible by assumption. □

### 2.3 Detailed Reduction ℬ₁ (IND-CPA)

**Construction:**

```
Adversary ℬ₁ against Π_FHE IND-CPA:
Input: Public key pk_FHE from IND-CPA challenger

1. Run 𝒜₁ to get (x₀, x₁, state)
2. Send (x₀, x₁) to IND-CPA challenger
3. Receive challenge ciphertext ct* (encrypts x_b for random b)
4. Generate ZKP keys: (ek_ZKP, vk_ZKP) ← Setup(1^λ, ℛ_Range)
5. If real protocol mode:
      - Generate proof: π ← Prove(ek_ZKP, (H_b, h_C), (x_b, σ))
   Else (simulated mode):
      - Simulate proof: π ← Sim(vk_ZKP, (H_b, h_C))
6. Compute (if needed): ct_result ← Eval(pk_FHE, f, ct*)
7. Give view = (ct*, π, H_b, h_C, ct_result) to 𝒜₂
8. Receive b' ← 𝒜₂(view, state)
9. Output b'
```

**Analysis:**
- If ct* encrypts x_b, this is Game 0/1 (depending on proof mode)
- If ct* is random, this is Game 2
- ℬ₁'s advantage equals 𝒜's distinguishing advantage
- Running time: poly(|𝒜|, λ)

### 2.4 Blockchain-Specific Privacy Considerations

**Public Observations:**
- Transaction sender address: reveals 𝒰's identity
- Gas consumption: leaks proof size/computation complexity
- Ciphertext size: leaks message space dimension
- Transaction ordering: leaks temporal information

**What Remains Private:**
- Actual input value x (under RLWE + pairing assumptions)
- Computation result f(x) (until user decrypts off-chain)
- Commitment randomness σ (zero-knowledge property)

**Formal Treatment:** See `leakage_model.md` for ℒ definition.

---

## 3. Soundness Analysis

### 3.1 Input Validation Soundness

**Theorem 3.1 (Computational Soundness)**

Let Π_ZKP be a computationally sound NIZK argument of knowledge. Then protocol Π provides computational soundness as defined in Definition 4.2 (security_model.md).

Formally, for any PPT adversary 𝒜 producing accepting proof (π, H, h_C):

```
Pr[Verify(vk_ZKP, (H, h_C), π) = 1 ∧ ∀w : ((H, h_C), w) ∉ ℛ_Range] ≤ ε_{sound}(λ)
```

where ε_{sound}(λ) ∈ negl(λ) is the soundness error of Π_ZKP.

### 3.2 Proof Argument

**By Knowledge Soundness of Groth16:**

If adversary 𝒜 produces accepting proof π, then by knowledge soundness property, there exists an efficient extractor 𝒦 such that:

```
Pr[(x, σ) ← 𝒦^𝒜(ek_ZKP) : Verify(vk_ZKP, (H, h_C), π) = 1 
    ∧ ¬((H, h_C), (x, σ)) ∈ ℛ_Range] ≤ ε_{know}(λ)
```

**Relation ℛ_Range enforces:**
1. Range constraint: 0 ≤ x ≤ R (via LessEqThan(32) circuit)
2. Commitment binding: H = Poseidon(x, σ, h_C)

**Therefore:**
- If proof accepts, extractor recovers (x, σ)
- If relation holds, then 0 ≤ x ≤ R
- Probability of forgery ≤ ε_{know}(λ) + ε_{collision}(λ)

where ε_{collision}(λ) is Poseidon collision probability (negligible).

### 3.3 Anti-Replay Protection

**Mechanism:** Context binding via h_C = H(chainID, addr, opType, reqID)

**Theorem 3.2 (Anti-Replay)**

Protocol Π provides anti-replay protection (Definition 4.4) if:
1. Hash function H is collision-resistant
2. Blockchain 𝔹 maintains reqID uniqueness per context

**Proof Sketch:**

Suppose adversary 𝒜 attempts replay:
- Original submission: (π, H, h_C) where h_C binds to reqID₁
- Replay attempt: (π', H', h_C') where h_c' binds to reqID₁

**Case 1:** h_C' = h_C
- Same context → blockchain rejects (duplicate reqID)

**Case 2:** h_C' ≠ h_C
- Different context → proof verification fails:
  ```
  Verify(vk_ZKP, (H, h_C'), π) = 0
  ```
- Because π proves H = Poseidon(x, σ, h_C), not H = Poseidon(x, σ, h_C')

**Case 3:** H' ≠ H, h_C' = h_C
- Requires finding (x', σ') ≠ (x, σ) with:
  ```
  Poseidon(x', σ', h_C) = Poseidon(x, σ, h_C)
  ```
- Probability ≤ ε_{collision}(λ) ∈ negl(λ)

All cases have negligible success probability. □

---

## 4. Limitations of Composition

### 4.1 What Composition Does NOT Provide

**Limitation 1: Verifiable FHE Computation**

Composition provides:
- ✅ Input x is validated (in range [0, R])
- ✅ Computation is on encrypted data (FHE privacy)

Composition does NOT provide:
- ❌ Proof that operator 𝒪 computed f correctly
- ❌ Proof that ct_result = Eval(pk_FHE, f, ct)

**Mitigation:** Trust assumption on operator 𝒪 (honest-but-curious model).

**Future Work:** Add verifiable FHE via:
- zkFHE: ZKP for FHE evaluation [ACNS 2020]
- Recursive SNARKs: Prove computation steps
- Multi-party FHE: Distributed computation with checks

**Limitation 2: Ciphertext-Commitment Binding**

Composition provides:
- ✅ Proof that plaintext x ∈ [0, R]
- ✅ Ciphertext ct encrypts some value

Composition does NOT directly prove:
- ❌ ct encrypts the same x from the proof

**Why:** Proof uses x, ciphertext encrypts x, but no cryptographic binding between π and ct.

**Practical Mitigation:**
- User 𝒰 generates both (same x input)
- Attack requires user to cheat themselves
- Relevant if multiple parties involved

**Formal Solution:** Add proof of plaintext knowledge (PoP) showing:
```
∃ (x, r) : ct = Enc(pk_FHE, x; r) ∧ H = Poseidon(x, σ, h_C)
```

This is feasible but not implemented (engineering complexity vs. threat model).

**Limitation 3: Approximate Correctness Only**

CKKS provides:
- ✅ Approximate correctness: |Dec(Eval(Enc(x))) - f(x)| ≤ ε
- ❌ Perfect correctness: Dec(Eval(Enc(x))) = f(x)

**Implication:** Composition inherits approximate correctness.

**See:** `correctness_theorem.md` for formal error analysis.

### 4.2 Trusted Setup Dependence

**Groth16 Trusted Setup:**

Security relies on:
```
(ek_ZKP, vk_ZKP) ← Setup(1^λ, ℛ_Range)
```

**Assumption:** Setup performed honestly, "toxic waste" (random τ) destroyed.

**If toxic waste compromised:**
- Adversary can create proofs for false statements
- Soundness (Theorem 3.1) breaks completely
- FHE privacy unaffected (separate assumption)

**Mitigation Strategies:**

1. **Multi-Party Computation (MPC) Ceremony:**
   - Setup = Setup₁ ∘ Setup₂ ∘ ... ∘ Setupₙ
   - Security if ANY party honest
   - Used in practice: Zcash Sapling, Ethereum Semaphore

2. **Universal SNARKs (No Trusted Setup):**
   - PLONK: Universal setup (circuit-independent)
   - Halo2: No setup (recursion-based)
   - STARKs: No setup (hash-based)
   - Trade-off: Larger proofs or higher verification cost

3. **Transparency:**
   - Publish ceremony transcript
   - Enable public verification
   - Document in `docs/limitations.md`

**Our Approach:** 
- Used Hermez perpetual Powers of Tau (public MPC)
- Added local contribution (defense in depth)
- Documented limitation explicitly

### 4.3 Leakage Beyond Encryption

**Blockchain Leakage:**

Even with perfect cryptography, blockchain reveals:
- ℒ_size: Ciphertext sizes (CKKS: ≈ 6KB per ct)
- ℒ_gas: Gas consumption (proof verification: ≈ 100K gas)
- ℒ_time: Transaction timestamps
- ℒ_addr: Sender/receiver addresses
- ℒ_freq: Transaction frequency patterns

**This is unavoidable** in public blockchain execution.

**Formal Treatment:** See `leakage_model.md` for complete ℒ definition.

**Comparison to Private Channels:**
- Private computation (AWS, TEE): Minimal leakage
- MPC protocols: Only output revealed (ideal functionality)
- Blockchain: Public execution inherently leaks metadata

**Design Choice:** Accept unavoidable leakage ℒ, protect payload privacy.

---

## 5. Composition Security Summary

### 5.1 What We Prove (Reduction-Based Arguments)

✅ **Input Privacy (Theorem 2.1)**
- Reduction to FHE IND-CPA + ZKP zero-knowledge
- Adversary advantage bounded by cryptographic assumptions

✅ **Soundness (Theorem 3.1)**  
- Reduction to Groth16 knowledge soundness
- Invalid inputs rejected with overwhelming probability

✅ **Anti-Replay (Theorem 3.2)**
- Based on commitment binding + blockchain uniqueness
- Replay attacks fail with overwhelming probability

### 5.2 What We Assume

**Cryptographic:**
- RLWE hardness (for FHE)
- Pairing hardness: q-PKE, q-SDH (for Groth16)
- Poseidon collision resistance (for commitments)

**Operational:**
- Operator 𝒪 honest-but-curious (no malicious computation)
- Trusted setup ceremony honest (no toxic waste compromise)
- Blockchain consensus secure (no 51% attacks)

**Computational:**
- Adversaries are PPT (polynomial-time bounded)
- No quantum adversaries (Groth16 not PQ-secure)
- No side-channel attacks (standard model)

### 5.3 Comparison to Universal Composability

**Our Approach:** Game-based reductions
- ✅ Sufficient for confidentiality + soundness
- ✅ Standard in applied cryptography
- ✅ Matches implementation complexity

**UC Framework Alternative:**
- Define ideal functionality ℱ_FHE+ZKP
- Prove real protocol Π realizes ℱ
- Obtain automatic composition guarantees

**Why We Don't Use UC:**
1. Blockchain not naturally modeled in UC (global state)
2. No additional security guarantees for our setting
3. Significantly more complex formalism
4. Game-based proofs are standard for FHE + NIZK

**Future Extension:** UC proof is possible if needed for composition with other protocols.

---

## 6. Formal Composition Theorem (Statement)

**Theorem 6.1 (Main Composition Theorem)**

Let λ be a security parameter. Let:
- Π_FHE = (KeyGen, Enc, Dec, Eval) be an IND-CPA secure FHE scheme
- Π_ZKP = (Setup, Prove, Verify) be a computationally sound zero-knowledge NIZK
- H: {0,1}* → {0,1}^λ be a collision-resistant hash function
- Π = Π_IV ∘ Π_FC be the composed protocol (Definition 2.3, security_model.md)

Then for all PPT adversaries 𝒜:

1. **Input Privacy:**
   ```
   Adv^{priv}_Π,𝒜(λ) ≤ Adv^{ind-cpa}_{Π_FHE}(λ) + Adv^{zk}_{Π_ZKP}(λ) + negl(λ)
   ```

2. **Soundness:**
   ```
   Pr[𝒜 produces accepting proof for x ∉ [0, R]] ≤ ε_{sound}(λ) + ε_{collision}(λ)
   ```

3. **Anti-Replay:**
   ```
   Pr[𝒜 replays valid proof in different context] ≤ ε_{collision}(λ)
   ```

All error terms are negligible in λ under stated cryptographic assumptions.

**Proof:** By Theorems 2.1, 3.1, 3.2 and hybrid argument. □

---

## 7. Practical Security Analysis

### 7.1 Concrete Security Parameters

**λ = 128 bit security:**

**CKKS FHE:**
- RLWE dimension: N = 16384
- Modulus: log q ≈ 438 bits
- Error distribution: discrete Gaussian σ = 3.2
- **Estimated security:** 129 bits (lattice-estimator)

**Groth16 SNARK:**
- Curve: BN254 (Barreto-Naehrig at 254-bit prime)
- **Estimated security:** 128 bits (2017), ~100 bits (2023 estimates)
- **Note:** BN curves losing security to Tower NFS attacks

**Poseidon Hash:**
- Field: BN254 scalar field
- Width: t = 5, rounds: R_F = 8, R_P = 57
- **Estimated security:** 128 bits (algebraic attacks)

**Overall Security:** Min(129, 100, 128) ≈ **100 bits** (bottleneck: BN254)

**Recommendation:** For long-term security, migrate to BLS12-381 curve (~128 bits resistant to NFS).

### 7.2 Performance vs Security Trade-offs

| Parameter | Security Impact | Performance Impact |
|-----------|----------------|-------------------|
| Larger N (RLWE) | +security | +computation, +ciphertext size |
| Larger log q | -security | +precision, +noise growth |
| More ZKP constraints | No direct impact | +proving time, +verification gas |
| Stronger curve (BLS12-381) | +security | +pairing time, +proof size |

**Our Choices:**
- N = 16384: Standard secure CKKS parameter
- BN254: Groth16 standard (gas-efficient on Ethereum)
- Range [0, 1M]: 32-bit comparator (2048 constraints)

### 7.3 Attack Vectors and Defenses

**Attack 1: Break RLWE → Learn x from ct**
- **Defense:** Use standard N = 16384, log q ≈ 438
- **Status:** Believed ~129-bit secure

**Attack 2: Break Groth16 Soundness → Forge proof for invalid x**
- **Defense:** Honest trusted setup, use MPC ceremony
- **Status:** ~100-bit secure (BN254), trusted setup critical

**Attack 3: Find Poseidon Collision → Bind different x to same H**
- **Defense:** Use full 128-bit security parameters
- **Status:** Believed ~128-bit secure

**Attack 4: Compromise sk_FHE → Decrypt ciphertexts**
- **Defense:** Key management (hardware wallet, HSM)
- **Status:** Out of scope (secure key storage)

**Attack 5: Replay proof in different context**
- **Defense:** Context binding h_C = H(chainID, addr, opType, reqID)
- **Status:** Protected by collision resistance + blockchain uniqueness

---

## 8. References

### Composition Theory
1. **Canetti, R.** "Security and Composition of Multiparty Cryptographic Protocols." Journal of Cryptology, 2000.
2. **Maurer, U.** "Constructive Cryptography – A New Paradigm for Security Definitions and Proofs." TOSCA 2011.

### FHE Security
3. **Brakerski, Z., Gentry, C., Vaikuntanathan, V.** "(Leveled) Fully Homomorphic Encryption without Bootstrapping." ITCS 2012.
4. **Cheon, J. H., Kim, A., Kim, M., Song, Y.** "Homomorphic Encryption for Arithmetic of Approximate Numbers." ASIACRYPT 2017.

### ZKP Security
5. **Groth, J.** "On the Size of Pairing-based Non-interactive Arguments." EUROCRYPT 2016.
6. **Bowe, S., Gabizon, A., Miers, I.** "Scalable Multi-party Computation for zk-SNARK Parameters in the Random Beacon Model." IACR ePrint 2017/1050.

### Blockchain Cryptography
7. **Bünz, B., Bootle, J., Boneh, D., et al.** "Bulletproofs: Short Proofs for Confidential Transactions and More." IEEE S&P 2018.
8. **Ben-Sasson, E., Chiesa, A., et al.** "Zerocash: Decentralized Anonymous Payments from Bitcoin." IEEE S&P 2014.

---

**Next:** See `leakage_model.md` for explicit leakage function ℒ definition and analysis.
