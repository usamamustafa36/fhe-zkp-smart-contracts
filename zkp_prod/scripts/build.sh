#!/bin/bash
#
# Production ZKP Build Script
# ============================
#
# Compiles Circom circuit and generates all cryptographic artifacts:
# - R1CS (Rank-1 Constraint System)
# - WASM witness generator
# - zkey (proving/verification keys via Groth16 setup)
# - Solidity verifier contract
# - Verification key (JSON)
#
# PREREQUISITES:
#   Run ./zkp_prod/scripts/setup.sh first
#
# USAGE:
#   ./zkp_prod/scripts/build.sh
#
# OUTPUT:
#   zkp_prod/artifacts/ - All generated files
#   zkp_prod/contracts/Verifier.sol - Solidity verifier
#
# SECURITY:
#   - Phase 2 contribution uses entropy from /dev/urandom
#   - Artifacts hashed with SHA256 for integrity verification
#   - Toxic waste from setup is discarded

set -e

CIRCUIT="range_commit"
BUILD_DIR="zkp_prod/artifacts"
CIRCUIT_DIR="zkp_prod/circuits"
CONTRACT_DIR="zkp_prod/contracts"

echo "🔨 Building Production ZKP Circuit: $CIRCUIT"
echo "================================================"

# Navigate to project root
cd "$(dirname "$0")/../.."

# Create build directory
mkdir -p "$BUILD_DIR"
mkdir -p "$CONTRACT_DIR"

# =========================================================================
# STEP 0: Verify Dependencies
# =========================================================================

echo ""
echo "[0/7] Verifying dependencies..."

if [ ! -d "zkp_prod/node_modules/circomlib" ]; then
    echo "   ⚠️  node_modules missing or incomplete. Running npm install..."
    cd zkp_prod && npm install && cd ..
fi

# Confirm poseidon.circom is resolvable
POSEIDON_PATH="zkp_prod/node_modules/circomlib/circuits/poseidon.circom"
if [ ! -f "$POSEIDON_PATH" ]; then
    echo "   ❌ Error: poseidon.circom not found at $POSEIDON_PATH"
    echo "      Ensure circomlib is installed correctly."
    exit 1
fi

echo "   ✅ circomlib: OK"

# =========================================================================
# STEP 0: Verify Dependencies
# =========================================================================

echo ""
echo "[0/7] Verifying dependencies..."

if [ ! -d "zkp_prod/node_modules/circomlib" ]; then
    echo "   ⚠️  node_modules missing or incomplete. Running npm install..."
    cd zkp_prod && npm install && cd ..
fi

# Confirm poseidon.circom is resolvable
POSEIDON_PATH="zkp_prod/node_modules/circomlib/circuits/poseidon.circom"
if [ ! -f "$POSEIDON_PATH" ]; then
    echo "   ❌ Error: poseidon.circom not found at $POSEIDON_PATH"
    echo "      Ensure circomlib is installed correctly."
    exit 1
fi

echo "   ✅ circomlib: OK"

# =========================================================================
# STEP 1: Compile Circuit
# =========================================================================

echo ""
echo "[1/7] Compiling Circom circuit..."

circom "$CIRCUIT_DIR/$CIRCUIT.circom" \
       --r1cs \
       --wasm \
       --sym \
       --output "$BUILD_DIR" \
       -l zkp_prod/node_modules \
       --verbose

echo "   ✅ Circuit compiled"
echo "   - R1CS: $BUILD_DIR/$CIRCUIT.r1cs"
echo "   - WASM: $BUILD_DIR/${CIRCUIT}_js/$CIRCUIT.wasm"

# =========================================================================
# STEP 2: Circuit Info
# =========================================================================

echo ""
echo "[2/7] Analyzing circuit..."

snarkjs r1cs info "$BUILD_DIR/$CIRCUIT.r1cs"

# =========================================================================
# STEP 3: Powers of Tau Setup (Phase 2)
# =========================================================================

echo ""
echo "[3/7] Running Powers of Tau Phase 2 (circuit-specific)..."

snarkjs groth16 setup \
        "$BUILD_DIR/$CIRCUIT.r1cs" \
        "$CIRCUIT_DIR/powersOfTau28_hez_final_12.ptau" \
        "$BUILD_DIR/${CIRCUIT}_0000.zkey"

echo "   ✅ Phase 2 setup complete"

# =========================================================================
# STEP 4: Contribute to Phase 2 (Add Entropy)
# =========================================================================

echo ""
echo "[4/7] Contributing entropy to Phase 2..."
echo "   (This adds randomness from this machine)"

# Use /dev/urandom for entropy
dd if=/dev/urandom bs=32 count=1 2>/dev/null | base64 | \
snarkjs zkey contribute \
        "$BUILD_DIR/${CIRCUIT}_0000.zkey" \
        "$BUILD_DIR/${CIRCUIT}_0001.zkey" \
        --name="Thesis Production Contribution $(date +%Y%m%d)" \
        -e

echo "   ✅ Entropy contribution complete"
echo "   ⚠️  Toxic waste discarded (zkey_0000 will be deleted)"

# Delete intermediate zkey (contains toxic waste)
rm "$BUILD_DIR/${CIRCUIT}_0000.zkey"

# =========================================================================
# STEP 5: Export Verification Key
# =========================================================================

echo ""
echo "[5/7] Exporting verification key..."

snarkjs zkey export verificationkey \
        "$BUILD_DIR/${CIRCUIT}_0001.zkey" \
        "$BUILD_DIR/verification_key.json"

echo "   ✅ Verification key exported"
echo "   - File: $BUILD_DIR/verification_key.json"

# =========================================================================
# STEP 6: Generate Solidity Verifier
# =========================================================================

echo ""
echo "[6/7] Generating Solidity verifier contract..."

snarkjs zkey export solidityverifier \
        "$BUILD_DIR/${CIRCUIT}_0001.zkey" \
        "$CONTRACT_DIR/Verifier.sol"

echo "   ✅ Solidity verifier generated"
echo "   - File: $CONTRACT_DIR/Verifier.sol"

# =========================================================================
# STEP 7: Compute Artifact Hashes (Integrity Verification)
# =========================================================================

echo ""
echo "[7/7] Computing artifact hashes (SHA256)..."

cd "$BUILD_DIR"

# Compute SHA256 hashes
{
    echo "# ZKP Artifact Hashes (SHA256)"
    echo "# Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "# Version: v1.0.0"
    echo ""
    sha256sum verification_key.json
    sha256sum ${CIRCUIT}_0001.zkey
    sha256sum ${CIRCUIT}_js/${CIRCUIT}.wasm
} > circuit_hashes.txt

echo "   ✅ Artifact hashes computed"
cat circuit_hashes.txt

# Return to project root
cd ../..

# =========================================================================
# Build Summary
# =========================================================================

echo ""
echo "================================================"
echo "✅ Build Complete!"
echo "================================================"
echo ""
echo "Generated Artifacts:"
echo "  📁 zkp_prod/artifacts/"
echo "     - range_commit.r1cs (constraint system)"
echo "     - range_commit_0001.zkey (proving key)"
echo "     - range_commit.wasm (witness generator)"
echo "     - verification_key.json (verifier key)"
echo "     - circuit_hashes.txt (integrity hashes)"
echo ""
echo "  📁 zkp_prod/contracts/"
echo "     - Verifier.sol (Solidity on-chain verifier)"
echo ""
echo "Next Steps:"
echo "  1. Review artifact hashes in circuit_hashes.txt"
echo "  2. Test proof generation: see zkp_prod/docs/OPERATIONS.md"
echo "  3. Deploy Verifier.sol to testnet"
echo ""
echo "⚠️  SECURITY NOTE:"
echo "   - Artifact hashes pinned for integrity verification"
echo "   - Use these hashes in production integrity checks"
echo "   - Trusted setup used Hermez Powers of Tau + local contribution"
echo ""
