# ZKP Setup Guide

This guide ensures a reproducible and production-safe setup of the ZKP subsystem.

## 📋 Prerequisites

- **Node.js**: v18.x or higher
- **npm**: v9.x or higher
- **Circom**: v2.1.x or higher (installed via `setup.sh`)
- **Disk Space**: ~500MB (for Phase 1 Powers of Tau)

## 🛠️ Installation Steps

### 1. Unified Setup
Run the automated setup script from the project root:
```bash
./zkp_prod/scripts/setup.sh
```

### 2. Manual Verification
If the automated script fails, follow these steps:

#### A. Install Circom
```bash
curl -L https://github.com/iden3/circom/releases/latest/download/circom-linux-amd64 -o /usr/local/bin/circom
chmod +x /usr/local/bin/circom
```

#### B. Install local dependencies
```bash
cd zkp_prod
npm install
```

#### C. Download Powers of Tau
```bash
wget https://storage.googleapis.com/zkevm/ptau/powersOfTau28_hez_final_12.ptau -O circuits/powersOfTau28_hez_final_12.ptau
```

## 🔒 Reproducibility Note

All dependencies are pinned in `zkp_prod/package.json`:
- `circomlib`: 2.0.5
- `snarkjs`: 0.7.0

The circuit includes are specified relative to `node_modules` and compiled using the `-l` flag to ensure no reliance on global environment state.

## 🏁 Verification

Confirm the build works:
```bash
./zkp_prod/scripts/build.sh
```
Check that artifacts appear in `zkp_prod/artifacts/`.
