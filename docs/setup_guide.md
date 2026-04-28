# 🔗 Blockchain Setup Guide: Local vs Sepolia

This guide explains how to use both **Local Blockchain (Ganache)** and **Sepolia Public Testnet** for the FHE Smart Contract demo.

---

## 📋 **Two Options Available**

### **Option 1: Local Blockchain (Ganache)** - Private
- ✅ No internet required
- ✅ Pre-funded accounts (100 ETH each)
- ✅ Fast transactions
- ✅ Perfect for testing
- ⚠️  Transactions are local only (not on public blockchain)

### **Option 2: Sepolia Public Testnet** - Public
- ✅ Real public blockchain
- ✅ Verifiable on Etherscan
- ✅ Impressive for thesis demo
- ⚠️  Requires test ETH from faucet
- ⚠️  Requires internet connection

---

## 🚀 **Quick Start**

### **For Local Blockchain:**

```bash
# 1. Setup local blockchain (one-time)
./setup_local_blockchain.sh

# 2. Start Ganache (in separate terminal)
./blockchain/local/start_ganache.sh

# 3. Run demo with local blockchain
python demo_with_network_selector.py --network local
```

### **For Sepolia Public Testnet:**

```bash
# 1. Run demo with Sepolia
python demo_with_network_selector.py --network sepolia

# 2. If you need test ETH:
python get_sepolia_eth.py
# Then get ETH from: https://sepoliafaucet.com
```

---

## 🔧 **Detailed Setup**

### **Local Blockchain Setup (Ganache)**

#### **Step 1: Install Dependencies**

```bash
# Install Node.js (if not installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Ganache CLI
sudo npm install -g ganache
```

#### **Step 2: Run Setup Script**

```bash
./setup_local_blockchain.sh
```

This will:
- Install Ganache (if needed)
- Create configuration files
- Create startup scripts

#### **Step 3: Start Ganache**

**Option A: Using helper script**
```bash
python blockchain/local_blockchain_helper.py start
```

**Option B: Manual start**
```bash
./blockchain/local/start_ganache.sh
```

**Option C: Direct command**
```bash
ganache --host 127.0.0.1 --port 8545 --networkId 1337 --accounts 2 --defaultBalanceEther 100
```

#### **Step 4: Verify Ganache is Running**

```bash
python blockchain/local_blockchain_helper.py status
```

Expected output:
```
✅ Ganache is running on http://127.0.0.1:8545
   Current Block: [number]
```

#### **Step 5: View Pre-funded Accounts**

```bash
python blockchain/local_blockchain_helper.py accounts
```

You'll see accounts with 100 ETH each.

#### **Step 6: Run Demo**

```bash
python demo_with_network_selector.py --network local
```

---

### **Sepolia Public Testnet Setup**

#### **Step 1: Get Test ETH**

```bash
# Check your account
python get_sepolia_eth.py
```

This will show:
- Your account address
- Current balance
- Instructions to get test ETH

#### **Step 2: Get Test ETH from Faucet**

1. Go to: https://sepoliafaucet.com
2. Enter your account address (from Step 1)
3. Click "Send Me ETH"
4. Wait 1-2 minutes

**Alternative Faucets:**
- https://www.alchemy.com/faucets/ethereum-sepolia
- https://faucet.quicknode.com/ethereum/sepolia

#### **Step 3: Verify Balance**

```bash
python get_sepolia_eth.py
```

You should see balance > 0 ETH.

#### **Step 4: Run Demo**

```bash
python demo_with_network_selector.py --network sepolia
```

---

## 📊 **Comparison Table**

| Feature | Local (Ganache) | Sepolia (Public) |
|---------|----------------|------------------|
| **Setup Time** | 5 minutes | 2 minutes |
| **Internet Required** | ❌ No | ✅ Yes |
| **Test ETH Needed** | ❌ No | ✅ Yes |
| **Transaction Speed** | ⚡ Instant | 🐌 10-30 seconds |
| **Verifiable** | ❌ No | ✅ Yes (Etherscan) |
| **Cost** | Free | Free (test ETH) |
| **Best For** | Testing | Thesis Demo |
| **Privacy** | Private | Public |
| **Pre-funded Accounts** | ✅ Yes (100 ETH) | ❌ No |

---

## 🎯 **Which One to Use?**

### **Use Local Blockchain (Ganache) if:**
- ✅ You're testing the system
- ✅ You don't have internet
- ✅ You want fast transactions
- ✅ You don't need public verification
- ✅ You want to avoid faucet issues

### **Use Sepolia Public Testnet if:**
- ✅ You're presenting to thesis committee
- ✅ You want verifiable transactions
- ✅ You want to show real blockchain integration
- ✅ You have test ETH available
- ✅ You want maximum credibility

---

## 🔄 **Switching Between Networks**

The demo supports switching between networks:

```bash
# Switch to local
python demo_with_network_selector.py --network local

# Switch to Sepolia
python demo_with_network_selector.py --network sepolia
```

---

## 🛠️ **Troubleshooting**

### **Local Blockchain Issues**

**Problem: Ganache not starting**
```bash
# Check if port 8545 is in use
lsof -i :8545

# Kill process if needed
pkill -f ganache

# Restart Ganache
python blockchain/local_blockchain_helper.py start
```

**Problem: Connection refused**
```bash
# Verify Ganache is running
python blockchain/local_blockchain_helper.py status

# If not running, start it
python blockchain/local_blockchain_helper.py start
```

### **Sepolia Issues**

**Problem: No test ETH**
```bash
# Check balance
python get_sepolia_eth.py

# Get ETH from faucet
# https://sepoliafaucet.com
```

**Problem: Connection timeout**
- Check internet connection
- Verify Infura API key is correct
- Try again (network may be busy)

---

## 📝 **Demo Commands Summary**

```bash
# Local Blockchain Demo
python demo_with_network_selector.py --network local

# Sepolia Public Testnet Demo
python demo_with_network_selector.py --network sepolia

# Check local blockchain status
python blockchain/local_blockchain_helper.py status

# Check Sepolia account
python get_sepolia_eth.py
```

---

## 🎓 **For Thesis Presentation**

**Recommended Approach:**

1. **Setup both** (local + Sepolia)
2. **Use Local for testing** (fast, reliable)
3. **Use Sepolia for presentation** (verifiable, impressive)
4. **Have backup plan** (if Sepolia fails, switch to local)

**Presentation Script:**
```
1. Show local blockchain (fast demo)
2. Switch to Sepolia (real blockchain)
3. Show transaction on Etherscan
4. Explain both options
```

---

## ✅ **Quick Verification**

**Test Local Blockchain:**
```bash
python blockchain/local_blockchain_helper.py status
# Should show: ✅ Ganache is running
```

**Test Sepolia:**
```bash
python get_sepolia_eth.py
# Should show: ✅ Connected to SEPOLIA
```

---

## 🚀 **Ready to Demo!**

Both blockchain options are now set up. Choose the one that best fits your needs:

- **Local**: Fast, private, no setup hassle
- **Sepolia**: Public, verifiable, impressive for thesis

Good luck with your thesis presentation! 🎓

