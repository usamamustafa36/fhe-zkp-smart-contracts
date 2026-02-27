#!/usr/bin/env python3
"""
Local Blockchain Simulator: Python-based local blockchain for FHE demo
Doesn't require Ganache installation - pure Python implementation
"""

import json
import time
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from web3 import Web3
from eth_account import Account
from eth_utils import to_hex

class LocalBlockchainSimulator:
    """
    Python-based local blockchain simulator.
    Simulates blockchain behavior without requiring Ganache.
    """
    
    def __init__(self):
        """Initialize local blockchain simulator."""
        self.chain_id = 1337
        self.network_name = "local_simulator"
        self.block_number = 1
        self.transactions = []
        self.accounts = []
        self.balances = {}
        
        # Create pre-funded accounts
        self._create_prefunded_accounts()
        
        print(f"✅ Local Blockchain Simulator Initialized")
        print(f"   Network: {self.network_name}")
        print(f"   Chain ID: {self.chain_id}")
        print(f"   Pre-funded Accounts: {len(self.accounts)}")
    
    def _create_prefunded_accounts(self):
        """Create pre-funded accounts with 100 ETH each."""
        for i in range(5):  # Create 5 accounts
            account = Account.create()
            self.accounts.append(account)
            self.balances[account.address] = 100 * 10**18  # 100 ETH in Wei
        
        print(f"📝 Pre-funded Accounts Created:")
        for i, account in enumerate(self.accounts[:3], 1):
            balance_eth = self.balances[account.address] / 10**18
            print(f"   Account {i}: {account.address[:10]}... ({balance_eth} ETH)")
    
    def get_accounts(self) -> List[str]:
        """Get list of account addresses."""
        return [acc.address for acc in self.accounts]
    
    def get_balance(self, address: str) -> int:
        """Get balance for an address."""
        return self.balances.get(address, 0)
    
    def submit_transaction(self, from_address: str, to_address: str, data: Dict, value: int = 0) -> Dict:
        """
        Submit a transaction to the local blockchain.
        
        Args:
            from_address: Sender address
            to_address: Recipient address (or contract)
            data: Transaction data
            value: ETH value to send
            
        Returns:
            Transaction receipt
        """
        # Generate transaction hash
        tx_data = json.dumps(data, sort_keys=True).encode()
        tx_hash = hashlib.sha256(tx_data + str(time.time()).encode()).hexdigest()
        
        # Create transaction
        transaction = {
            'hash': '0x' + tx_hash,
            'from': from_address,
            'to': to_address,
            'value': value,
            'data': data,
            'blockNumber': self.block_number,
            'blockHash': '0x' + hashlib.sha256(str(self.block_number).encode()).hexdigest(),
            'transactionIndex': len(self.transactions),
            'gasUsed': 21000,  # Standard gas for simple transaction
            'gasPrice': 20000000000,  # 20 gwei
            'status': 1,  # Success
            'timestamp': int(time.time())
        }
        
        # Add to transaction list
        self.transactions.append(transaction)
        self.block_number += 1
        
        return {
            'tx_hash': transaction['hash'],
            'block_number': transaction['blockNumber'],
            'gas_used': transaction['gasUsed'],
            'status': 'success',
            'network': self.network_name,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction by hash."""
        for tx in self.transactions:
            if tx['hash'] == tx_hash:
                return tx
        return None
    
    def get_all_transactions(self) -> List[Dict]:
        """Get all transactions."""
        return self.transactions
    
    def get_network_info(self) -> Dict:
        """Get network information."""
        return {
            'network': self.network_name,
            'chain_id': self.chain_id,
            'block_number': self.block_number,
            'total_transactions': len(self.transactions),
            'accounts': len(self.accounts)
        }

# Global simulator instance
_simulator = None

def get_local_simulator() -> LocalBlockchainSimulator:
    """Get or create local blockchain simulator instance."""
    global _simulator
    if _simulator is None:
        _simulator = LocalBlockchainSimulator()
    return _simulator

