#!/usr/bin/env python3
"""
Helper script to get Sepolia test ETH and check account balance
"""

from blockchain.real_blockchain_integration import RealBlockchainIntegration

def main():
    print("🔗 Sepolia Testnet Helper")
    print("=" * 50)
    
    # Create blockchain integration
    blockchain = RealBlockchainIntegration(network="sepolia")
    
    # Show account info
    print(f"📝 Your Account Address: {blockchain.account.address}")
    print(f"🔑 Your Private Key: {blockchain.account.key.hex()}")
    
    # Check balance
    balance = blockchain.get_account_balance()
    print(f"\n💰 Current Balance:")
    print(f"   └─ Address: {balance['address']}")
    print(f"   └─ Balance: {balance['balance_eth']:.6f} ETH")
    print(f"   └─ Balance: {balance['balance_wei']} Wei")
    
    if balance['balance_eth'] < 0.01:
        print(f"\n⚠️  Low Balance! You need Sepolia test ETH.")
        print(f"📋 Steps to get ETH:")
        print(f"   1. Go to: https://sepoliafaucet.com")
        print(f"   2. Enter your address: {blockchain.account.address}")
        print(f"   3. Click 'Send Me ETH'")
        print(f"   4. Wait a few minutes for confirmation")
        print(f"   5. Run this script again to check balance")
    else:
        print(f"\n✅ You have enough ETH to run the demo!")
        print(f"🚀 Run: python proper_fhe_demo.py")
    
    print(f"\n🔍 View your account on Sepolia:")
    print(f"   └─ https://sepolia.etherscan.io/address/{blockchain.account.address}")

if __name__ == "__main__":
    main() 