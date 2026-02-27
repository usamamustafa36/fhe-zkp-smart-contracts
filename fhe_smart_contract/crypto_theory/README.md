# Cryptographic Theory and Formal Analysis

**Status:** PhD-Level Applied Cryptography Research Component  
**Purpose:** Formal security analysis for FHE + ZKP composition in blockchain context

---

## Scope and Non-Claims

### What This Component Provides

✅ **Formal Security Model**
- Precise definitions of system participants, adversary capabilities, and security goals
- Follows standard cryptographic definitional framework (e.g., Bellare-Rogaway)

✅ **Composition Security Analysis**
- Reduction-based argument for FHE + ZKP composition
- Clear statement of cryptographic assumptions and their limitations

✅ **Explicit Leakage Model**
- Formal definition of leakage function ℒ
- Analysis of what information is leaked vs. protected in blockchain context

✅ **Correctness Theorem**
- Formal statement of CKKS correctness guarantees under bounded noise
- Error bounds and precision analysis

### What This Component Does NOT Provide

❌ **New Cryptographic Constructions**
- We use existing schemes (CKKS, Groth16) as black boxes
- No modifications to underlying cryptographic primitives

❌ **Formal Security Proofs**
- We provide reduction-based arguments and security analysis
- Full game-based proofs would require formal verification tools (e.g., EasyCrypt, CryptoVerif)

❌ **Post-Quantum Security**
- Groth16 SNARKs rely on pairing-based cryptography (not post-quantum)
- CKKS security based on RLWE (believed post-quantum, but not proven)

❌ **Byzantine Fault Tolerance**
- Analysis assumes honest-but-curious or malicious adversaries within computational bounds
- Does not address consensus-level attacks or blockchain-specific Byzantine scenarios

❌ **Side-Channel Protection**
- Analysis is in the standard model (no timing, power, or cache attacks)
- Implementation-level side channels are out of scope

---

## Academic Context

**Research Level:** PhD-level applied cryptography  
**Target Venues:** ACM CCS, USENIX Security, IEEE S&P, Crypto/Eurocrypt (applied track)  
**Mathematical Rigor:** Formal definitions + reduction-based arguments (not full proofs)

**Relationship to Implementation:**
- Theory components in `crypto_theory/` are standalone formal analysis
- Implementation in `zkp_prod/`, `crypto/`, `core/` is separate
- Empirical validation in `evaluation/` provides experimental evidence

---

## File Structure

```
crypto_theory/
├── README.md                    (this file)
├── security_model.md            Formal definitions of system, adversary, security goals
├── composition_analysis.md      Security argument for FHE + ZKP composition
├── leakage_model.md            Formal leakage function and analysis
├── correctness_theorem.md       CKKS correctness under bounded noise
└── notation.md                  Mathematical notation reference
```

---

## How to Read These Documents

### For Cryptographers
1. Start with `security_model.md` for formal definitions
2. Read `composition_analysis.md` for main security argument
3. Check `leakage_model.md` for practical leakage analysis
4. See `correctness_theorem.md` for CKKS-specific guarantees

### For Systems Researchers
1. Start with this README for scope
2. Read `leakage_model.md` for what blockchain reveals
3. Check `security_model.md` section 3 (security goals)
4. See `composition_analysis.md` section 4 (limitations)

### For Thesis Committee
- Theory: `crypto_theory/` (this directory)
- Implementation: `zkp_prod/`, `core/`, `crypto/`
- Evaluation: `evaluation/`
- All three components are necessary and complement each other

---

## Conservative Claims Philosophy

**We explicitly acknowledge:**
1. Security is conditional on standard cryptographic assumptions (RLWE, pairing hardness)
2. Composition analysis is a reduction-based argument, not a machine-checked proof
3. Leakage model identifies unavoidable blockchain-context leakage
4. Correctness is probabilistic and bounded by CKKS noise growth
5. Implementation details may introduce additional vulnerabilities not covered by theory

**We do NOT claim:**
- Unconditional security
- Zero leakage (we formalize what leaks)
- Perfect correctness (we bound errors)
- Side-channel resistance (standard model only)
- Post-quantum security (Groth16 component is not PQ)

---

## Integration with Existing Codebase

### Theory ↔ Implementation Correspondence

| Theoretical Component | Implementation | Validation |
|----------------------|----------------|------------|
| FHE scheme (CKKS) | `core/fhe_engine.py` (TenSEAL) | `crypto/correctness.py` |
| ZKP scheme (Groth16) | `zkp_prod/` (Circom + snarkjs) | `zkp_prod/tests/` |
| Leakage function ℒ | Blockchain gas analysis | `evaluation/cost_analysis.py` |
| Correctness theorem | Error tracking | `evaluation/performance.py` |

### Theory Complements Code
- **Theory defines WHAT security properties hold**
- **Code demonstrates HOW to achieve them in practice**
- **Evaluation shows THAT they work empirically**

---

## References to Foundational Work

### FHE Theory
- [CKKS17] Cheon, Kim, Kim, Song. "Homomorphic Encryption for Arithmetic of Approximate Numbers." ASIACRYPT 2017.
- [BGV12] Brakerski, Gentry, Vaikuntanathan. "Fully Homomorphic Encryption without Bootstrapping." ITCS 2012.

### ZKP Theory
- [Gro16] Groth. "On the Size of Pairing-based Non-interactive Arguments." EUROCRYPT 2016.
- [BCTV14] Ben-Sasson, Chiesa, Tromer, Virza. "Succinct Non-Interactive Zero Knowledge for a von Neumann Architecture." USENIX 2014.

### Composition
- [Can01] Canetti. "Universally Composable Security: A New Paradigm for Cryptographic Protocols." FOCS 2001.
- [BGW05] Boneh, Goh, Nissim. "Evaluating 2-DNF Formulas on Ciphertexts." TCC 2005.

---

## Academic Integrity Note

**This component represents original analysis** of the composition of existing cryptographic primitives (CKKS FHE and Groth16 SNARKs) in a novel blockchain context. 

**What is novel:**
- Formal model for FHE + ZKP composition in public blockchain setting
- Explicit leakage analysis for blockchain-specific information channels
- Security analysis accounting for public execution artifacts

**What is not novel (we build on):**
- CKKS security (assumed)
- Groth16 security (assumed)
- General composition frameworks (we apply, not invent)

---

## Future Work

### Theoretical Extensions
1. **Formal Verification:** Mechanize proofs in Coq/EasyCrypt/CryptoVerif
2. **Universal Composability:** Extend analysis to UC framework
3. **Post-Quantum Migration:** Analyze PLONK/STARK alternatives to Groth16
4. **Differential Privacy:** Add DP guarantees on top of cryptographic privacy

### Implementation Hardening
1. **Side-Channel Protection:** Constant-time implementations
2. **Verifiable FHE:** Add ZKPs for FHE computation correctness
3. **Multi-Party Setup:** Decentralize trusted setup ceremony
4. **Formal Implementation Verification:** Verify code matches theory

---

**For questions about cryptographic claims or notation, see individual files in this directory.**

**For questions about implementation details, see `zkp_prod/docs/SECURITY.md` and `crypto/threat_model.md`.**
