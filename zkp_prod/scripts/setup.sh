#!/bin/bash
#
# Production ZKP Setup Script
# ============================
#
# Installs all dependencies required for ZKP production system:
# - Circom compiler
# - snarkjs proof system
# - circomlib circuit library
# - Powers of Tau (trusted setup Phase 1)
#
# USAGE:
#   cd /home/ubuntu/Projects/THESIS/fhe_smart_contract
#   ./zkp_prod/scripts/setup.sh
#
# REQUIREMENTS:
#   - Node.js >= 18.0.0
#   - npm >= 9.0.0
#   - ~500MB disk space for Powers of Tau

set -e  # Exit on error

echo "🔧 Setting up Production ZKP System"
echo "===================================="

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js not found"
    echo "   Install: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Node.js >= 18 required (found: $(node -v))"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Navigate to project root
cd "$(dirname "$0")/../.."

# 1. Install global tools
echo ""
echo "📦 Installing Circom and snarkjs..."

# Try npm first
if npm install -g circomc@latest snarkjs@latest 2>/dev/null; then
    echo "   ✅ Installed via npm"
else
    echo "   ⚠️  npm installation failed, trying alternative..."
    
    # Fallback: Install circom from GitHub releases
    echo "   Installing circom from GitHub releases..."
    
    # Detect architecture
    if [[ $(uname -m) == "x86_64" ]]; then
        ARCH="linux-amd64"
    elif [[ $(uname -m) == "aarch64" ]]; then
        ARCH="linux-arm64"
    else
        ARCH="linux-amd64"  # Default
    fi
    
    # Download and install circom
    curl -L https://github.com/iden3/circom/releases/latest/download/circom-$ARCH -o /tmp/circom
    chmod +x /tmp/circom
    sudo mv /tmp/circom /usr/local/bin/circom
    
    # Install snarkjs with sudo
    sudo npm install -g snarkjs@latest
    
    echo "   ✅ Installed via GitHub releases"
fi

# 2. Install circuit libraries (Local)
echo ""
echo "📦 Installing circuit libraries locally..."
cd zkp_prod

# Ensure package.json exists (should have been created by previous step, but let's be safe)
if [ ! -f "package.json" ]; then
    echo "   ⚠️  package.json missing, creating default..."
    npm init -y 2>/dev/null || true
    npm install circomlib@2.0.5 snarkjs@0.7.0 --save
else
    echo "   Installing from pinned package.json..."
    npm install
fi

# Verify circomlib version
CIRCOMLIB_VERSION=$(npm list circomlib | grep circomlib | awk -F@ '{print $2}')
echo "   ✅ circomlib version: $CIRCOMLIB_VERSION"

# 3. Download Powers of Tau (Phase 1 trusted setup)
echo ""
echo "📦 Downloading Powers of Tau (Phase 1 Trusted Setup)..."
echo "   Source: iden3 GitHub (perpetual ceremony)"
echo "   Size: ~50MB"

PTAU_FILE="circuits/powersOfTau28_hez_final_12.ptau"

if [ -f "$PTAU_FILE" ] && [ -s "$PTAU_FILE" ]; then
    echo "   ✅ Powers of Tau already downloaded"
else
    # Remove empty file if exists
    rm -f "$PTAU_FILE"
    
    # Try primary source (iden3 GitHub)
    echo "   Trying primary source (iden3)..."
    if wget -q --show-progress \
         https://storage.googleapis.com/zkevm/ptau/powersOfTau28_hez_final_12.ptau \
         -O "$PTAU_FILE" 2>/dev/null; then
        echo "   ✅ Powers of Tau downloaded from Google Cloud"
    else
        # Fallback: Use smaller ceremony for testing
        echo "   ⚠️  Primary source failed, using alternative..."
        if wget -q --show-progress \
             https://github.com/iden3/snarkjs/raw/master/build/powersOfTau28_hez_final_08.ptau \
             -O "$PTAU_FILE" 2>/dev/null; then
            echo "   ✅ Powers of Tau downloaded (smaller ceremony)"
        else
            echo "   ❌ Download failed. You'll need to download manually"
            echo "      URL: https://github.com/iden3/snarkjs#7-prepare-phase-2"
            exit 1
        fi
    fi
fi

# 4. Verify installations
echo ""
echo "🔍 Verifying installations..."

if command -v circom &> /dev/null; then
    echo "   ✅ Circom: $(circom --version)"
else
    echo "   ❌ Circom installation failed"
    exit 1
fi

if command -v snarkjs &> /dev/null; then
    echo "   ✅ snarkjs: installed"
else
    echo "   ❌ snarkjs installation failed"
    exit 1
fi

if [ -d "node_modules/circomlib" ]; then
    echo "   ✅ circomlib: installed"
else
    echo "   ❌ circomlib installation failed"
    exit 1
fi

if [ -f "$PTAU_FILE" ]; then
    echo "   ✅ Powers of Tau: ready"
else
    echo "   ❌ Powers of Tau download failed"
    exit 1
fi

# 5. Create .gitignore for artifacts
echo ""
echo "📝 Creating .gitignore for ZKP artifacts..."

cat > .gitignore << 'EOF'
# ZKP Build Artifacts (regenerate with build.sh)
artifacts/*.r1cs
artifacts/*.zkey
artifacts/*.wasm
artifacts/*.wtns
artifacts/*_js/
artifacts/temp_*

# Keep these
!artifacts/verification_key.json
!artifacts/circuit_hashes.json

# Dependencies
node_modules/

# Temp files
*.log
.DS_Store
EOF

echo "   ✅ .gitignore created"

# Summary
echo ""
echo "===================================="
echo "✅ Setup Complete!"
echo "===================================="
echo ""
echo "Next steps:"
echo "  1. Build circuit:    ./zkp_prod/scripts/build.sh"
echo "  2. Test circuit:     npm test (in zkp_prod/)"
echo "  3. Generate proofs:  See zkp_prod/README.md"
echo ""
echo "Dependencies installed:"
echo "  - Circom (circuit compiler) - latest"
echo "  - snarkjs (proof system) - latest"
echo "  - circomlib 2.0.5 (circuit library)"
echo "  - Powers of Tau Phase 1 (trusted setup)"
echo ""
