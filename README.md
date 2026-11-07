# Privacy-Preserving Smart Contracts via FHE + ZKP

**Author:** Usama Mustafa
**Domain:** Applied cryptography · Blockchain · Privacy-preserving computation
**Stack:** Python · TenSEAL (CKKS) · Circom · Groth16 · Solidity · Sepolia

A working blockchain stack that combines fully homomorphic encryption with zero-knowledge proofs to execute smart-contract logic without revealing inputs, outputs, or intermediate state — and a formal leakage analysis quantifying the residual entropy that survives the protocol.

---

## What it does

- Encrypts contract inputs with **CKKS** (TenSEAL) before they ever touch the chain
- Computes contract logic homomorphically on the ciphertexts
- Generates a **Groth16** zero-knowledge range proof that each committed private input lies in [0, 1,000,000], bound to chain, contract, operation and request (the proof does **not** cover correctness of the CKKS computation; see `docs/limitations.md`)
- Submits the ciphertext result and the ZK proof to a Solidity verifier on Sepolia
- Performs **formal leakage characterisation** — entropy analysis on the ciphertext stream confirms >7.8 bits/byte (close to ideal randomness)

## Why

Privacy-preserving smart contracts are usually demonstrated with one technique. FHE alone leaks correctness; ZKP alone leaks inputs. Combining them gives input privacy *and* verified input validity (not verified execution) — but the combination is rarely measured against a leakage threat model. This repo does both.

## Layout

- `fhe_engine/` — CKKS scheme parameters, ciphertext lifecycle, key management
- `crypto/` — primitives, hashing, randomness
- `crypto_theory/` — notation and security model writeups
- `blockchain/` — Sepolia deployment, contract interaction, gas accounting
- `core/` — orchestration: ingest → FHE → ZK → submit → verify
- `zkp_prod/` — Groth16 circuits (Circom) and verifier contracts
- `evaluation/` — leakage analysis, benchmarks, entropy measurements
- `demo/` — runnable end-to-end demo
- `frontend_app.py` — minimal web UI
- `proposal_aligned_thesis.py` — reproducibility script tying results to the design document
- `setup_local_blockchain.sh` — local Hardhat / Anvil setup
- `run-everything.sh` — one-shot end-to-end run
- `run-full-evaluation.sh` — leakage + performance benchmarks
- `get_sepolia_eth.py` — testnet faucet helper

## Run

```bash
pip install -r requirements.txt
./setup_local_blockchain.sh   # local chain (optional, for offline runs)
./run-everything.sh            # FHE encrypt → compute → ZK prove → submit → verify
./run-full-evaluation.sh       # leakage + benchmark suite
```

Sepolia testnet ETH: `python get_sepolia_eth.py`.

## Results summary

- End-to-end privacy-preserving execution working on Sepolia testnet
- Ciphertext entropy >7.8 bits/byte (no statistical leakage detected at byte granularity)
- Groth16 proof generation and on-chain verification gas costs documented in `evaluation/`

## License

MIT
