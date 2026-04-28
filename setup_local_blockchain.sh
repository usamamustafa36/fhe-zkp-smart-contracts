#!/bin/bash
# Setup Local Blockchain for FHE Smart Contract Demo
# Uses Ganache for local Ethereum blockchain

echo "🔧 Setting up Local Blockchain for FHE Smart Contract Demo"
echo "=========================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Installing..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Installing..."
    sudo apt-get install -y npm
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"

# Install Ganache globally
if ! command -v ganache &> /dev/null; then
    echo "📦 Installing Ganache CLI..."
    sudo npm install -g ganache
else
    echo "✅ Ganache is already installed"
fi

# Create ganache config directory
mkdir -p ~/.ganache
mkdir -p blockchain/local

# Create Ganache configuration
cat > blockchain/local/ganache-config.js << 'EOF'
module.exports = {
    accounts: [
        {
            secretKey: '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d',
            balance: '100000000000000000000' // 100 ETH
        },
        {
            secretKey: '0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1',
            balance: '100000000000000000000' // 100 ETH
        }
    ],
    host: '127.0.0.1',
    port: 8545,
    network_id: 1337,
    gas: 6721975,
    gasPrice: 20000000000
};
EOF

# Create startup script
cat > blockchain/local/start_ganache.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Ganache Local Blockchain..."
echo "   RPC URL: http://127.0.0.1:8545"
echo "   Chain ID: 1337"
echo "   Network ID: 1337"
echo ""
echo "📝 Pre-funded Accounts:"
echo "   Account 1: 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1 (100 ETH)"
echo "   Account 2: 0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0 (100 ETH)"
echo ""
echo "⚠️  Keep this terminal open while running the demo"
echo "   Press Ctrl+C to stop Ganache"
echo ""

ganache \
    --host 127.0.0.1 \
    --port 8545 \
    --networkId 1337 \
    --gasLimit 6721975 \
    --gasPrice 20000000000 \
    --accounts 2 \
    --defaultBalanceEther 100 \
    --deterministic
EOF

chmod +x blockchain/local/start_ganache.sh

# Create stop script
cat > blockchain/local/stop_ganache.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Ganache..."
pkill -f ganache
echo "✅ Ganache stopped"
EOF

chmod +x blockchain/local/stop_ganache.sh

echo ""
echo "✅ Local Blockchain Setup Complete!"
echo ""
echo "📋 To start local blockchain:"
echo "   ./blockchain/local/start_ganache.sh"
echo ""
echo "📋 To stop local blockchain:"
echo "   ./blockchain/local/stop_ganache.sh"
echo ""
echo "📋 To use local blockchain in demo:"
echo "   python proper_fhe_demo.py --network local"
echo ""

