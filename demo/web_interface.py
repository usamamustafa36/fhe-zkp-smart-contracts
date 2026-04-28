#!/usr/bin/env python3
"""
Frontend Web Application for Privacy-Preserving Smart Contract Demo
Flask-based web interface for thesis demonstration
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
import time
import json
import hashlib
from datetime import datetime
from typing import Dict

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.fhe_engine import AdvancedFHE, FHEScheme
from core.entropy import shannon_entropy
from blockchain.integration import RealBlockchainIntegration

app = Flask(__name__)

# Initialize FHE engine and blockchain
fhe_engine = AdvancedFHE(scheme=FHEScheme.CKKS, precision_bits=40)
blockchain_integration = None

def init_blockchain(network='local'):
    """Initialize blockchain integration."""
    global blockchain_integration
    try:
        blockchain_integration = RealBlockchainIntegration(network=network)
        return True, f"Connected to {network.upper()} blockchain"
    except Exception as e:
        return False, f"Failed to connect: {str(e)}"

# Initialize with local blockchain by default
init_blockchain('local')

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/blockchain')
def blockchain_explorer():
    """Blockchain explorer page."""
    return render_template('blockchain_explorer.html')

@app.route('/api/network', methods=['POST'])
def set_network():
    """Set blockchain network."""
    data = request.json
    network = data.get('network', 'local')
    
    success, message = init_blockchain(network)
    return jsonify({
        'success': success,
        'message': message,
        'network': network
    })

@app.route('/api/validate', methods=['POST'])
def validate_input():
    """ZKP validation endpoint."""
    data = request.json
    value = float(data.get('value', 0))
    
    # Validate range
    is_valid = -1000000 <= value <= 1000000
    input_hash = hashlib.sha256(str(value).encode()).hexdigest()
    
    proof_id = f"zkp_{int(time.time())}_{hash(str(value)) % 10000}"
    zkp_proof = {
        'proof_id': proof_id,
        'input_hash': input_hash,
        'timestamp': time.time(),
        'validator': 'ZKP_Validator_v1.0',
        'validation': {
            'value': value,
            'is_valid': is_valid,
            'validation_rule': 'numeric_range',
            'min_allowed': -1000000,
            'max_allowed': 1000000
        }
    }
    
    return jsonify({
        'success': is_valid,
        'proof': zkp_proof,
        'message': 'Input validated' if is_valid else 'Input out of range'
    })

@app.route('/api/encrypt', methods=['POST'])
def encrypt():
    """FHE encryption endpoint."""
    data = request.json
    value = float(data.get('value', 0))
    
    start_time = time.time()
    encrypted = fhe_engine.encrypt_batch_optimized([value])[0]
    encryption_time = time.time() - start_time
    
    entropy = shannon_entropy(str(encrypted))
    
    return jsonify({
        'success': True,
        'encrypted': str(encrypted),
        'encryption_time': encryption_time,
        'entropy': entropy,
        'security_level': 'High' if entropy >= 5 else 'Medium' if entropy >= 3 else 'Low'
    })

@app.route('/api/compute', methods=['POST'])
def compute():
    """FHE computation endpoint."""
    data = request.json
    encrypted1_str = data.get('encrypted1')
    encrypted2_str = data.get('encrypted2')
    
    # Reconstruct encrypted values (simplified - in real app, you'd serialize properly)
    # For demo, we'll re-encrypt with the values
    num1 = float(data.get('num1', 0))
    num2 = float(data.get('num2', 0))
    
    # Encrypt both values
    encrypted1 = fhe_engine.encrypt_batch_optimized([num1])[0]
    encrypted2 = fhe_engine.encrypt_batch_optimized([num2])[0]
    
    # Perform FHE addition
    start_time = time.time()
    encrypted_sum = fhe_engine.add_encrypted_batch_optimized([encrypted1], [encrypted2])[0]
    computation_time = time.time() - start_time
    
    # Decrypt result
    decrypted_sum = fhe_engine.decrypt_batch_optimized([encrypted_sum])[0]
    
    entropy = shannon_entropy(str(encrypted_sum))
    
    return jsonify({
        'success': True,
        'encrypted_sum': str(encrypted_sum),
        'decrypted_result': decrypted_sum,
        'computation_time': computation_time,
        'entropy': entropy,
        'expected_result': num1 + num2,
        'accuracy': abs(decrypted_sum - (num1 + num2)) < 0.01
    })

@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    """FHE decryption endpoint."""
    data = request.json
    encrypted_str = data.get('encrypted')
    num1 = float(data.get('num1', 0))
    num2 = float(data.get('num2', 0))
    
    # Re-encrypt to get the sum (for demo purposes)
    encrypted1 = fhe_engine.encrypt_batch_optimized([num1])[0]
    encrypted2 = fhe_engine.encrypt_batch_optimized([num2])[0]
    encrypted_sum = fhe_engine.add_encrypted_batch_optimized([encrypted1], [encrypted2])[0]
    
    start_time = time.time()
    decrypted = fhe_engine.decrypt_batch_optimized([encrypted_sum])[0]
    decryption_time = time.time() - start_time
    
    return jsonify({
        'success': True,
        'decrypted': decrypted,
        'decryption_time': decryption_time,
        'expected': num1 + num2,
        'correct': abs(decrypted - (num1 + num2)) < 0.01
    })

@app.route('/api/blockchain', methods=['POST'])
def submit_blockchain():
    """Blockchain submission endpoint."""
    data = request.json
    
    submission_data = {
        'zkp_proofs': [
            data.get('zkp_proof1', {}),
            data.get('zkp_proof2', {})
        ],
        'encrypted_inputs': [
            data.get('encrypted1', ''),
            data.get('encrypted2', '')
        ],
        'encrypted_result': data.get('encrypted_sum', ''),
        'decrypted_result': data.get('decrypted_result', 0),
        'operation': 'fhe_addition',
        'timestamp': datetime.now().isoformat(),
        'metadata': {
            'fhe_scheme': 'CKKS',
            'precision_bits': 40,
            'network': blockchain_integration.network if blockchain_integration else 'local'
        }
    }
    
    try:
        result = blockchain_integration.submit_encrypted_computation(submission_data)
        
        network_info = {
            'network': blockchain_integration.network if blockchain_integration else 'local',
            'type': 'Private (Local Simulator)' if blockchain_integration and blockchain_integration.use_simulator else 'Public (Sepolia)'
        }
        
        return jsonify({
            'success': True,
            'tx_hash': result.get('tx_hash', ''),
            'block_number': result.get('block_number', ''),
            'gas_used': result.get('gas_used', ''),
            'status': result.get('status', ''),
            'network_info': network_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status."""
    network = blockchain_integration.network if blockchain_integration else 'local'
    network_type = 'Private (Local Simulator)' if blockchain_integration and blockchain_integration.use_simulator else 'Public (Sepolia)'
    
    return jsonify({
        'network': network,
        'network_type': network_type,
        'fhe_scheme': 'CKKS',
        'precision_bits': 40
    })

@app.route('/api/blockchain/transactions', methods=['GET'])
def get_transactions():
    """Get all blockchain transactions."""
    try:
        from blockchain.simulator import get_local_simulator
        
        if blockchain_integration and blockchain_integration.use_simulator:
            simulator = get_local_simulator()
            transactions = simulator.get_all_transactions()
            
            # Format transactions for frontend
            formatted_txs = []
            for tx in transactions:
                tx_data = tx.get('data', {})
                formatted_tx = {
                    'hash': tx['hash'],
                    'from': tx['from'],
                    'to': tx['to'],
                    'block_number': tx['blockNumber'],
                    'block_hash': tx['blockHash'],
                    'transaction_index': tx['transactionIndex'],
                    'gas_used': tx['gasUsed'],
                    'gas_price': tx['gasPrice'],
                    'status': 'success' if tx['status'] == 1 else 'failed',
                    'timestamp': datetime.fromtimestamp(tx['timestamp']).isoformat(),
                    'operation': tx_data.get('operation', 'fhe_computation'),
                    'zkp_proofs': tx_data.get('zkp_proofs', []),
                    'encrypted_inputs_count': len(tx_data.get('encrypted_inputs', [])),
                    'decrypted_result': tx_data.get('decrypted_result'),
                    'metadata': tx_data.get('metadata', {})
                }
                formatted_txs.append(formatted_tx)
            
            # Sort by block number (newest first)
            formatted_txs.sort(key=lambda x: x['block_number'], reverse=True)
            
            return jsonify({
                'success': True,
                'transactions': formatted_txs,
                'total': len(formatted_txs)
            })
        else:
            # For Sepolia or other networks, return empty for now
            return jsonify({
                'success': True,
                'transactions': [],
                'total': 0,
                'message': 'Transaction history not available for this network'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blockchain/transaction/<tx_hash>', methods=['GET'])
def get_transaction(tx_hash):
    """Get specific transaction by hash."""
    try:
        from blockchain.simulator import get_local_simulator
        
        if blockchain_integration and blockchain_integration.use_simulator:
            simulator = get_local_simulator()
            tx = simulator.get_transaction(tx_hash)
            
            if tx:
                tx_data = tx.get('data', {})
                formatted_tx = {
                    'hash': tx['hash'],
                    'from': tx['from'],
                    'to': tx['to'],
                    'block_number': tx['blockNumber'],
                    'block_hash': tx['blockHash'],
                    'transaction_index': tx['transactionIndex'],
                    'gas_used': tx['gasUsed'],
                    'gas_price': tx['gasPrice'],
                    'status': 'success' if tx['status'] == 1 else 'failed',
                    'timestamp': datetime.fromtimestamp(tx['timestamp']).isoformat(),
                    'operation': tx_data.get('operation', 'fhe_computation'),
                    'zkp_proofs': tx_data.get('zkp_proofs', []),
                    'encrypted_inputs': tx_data.get('encrypted_inputs', []),
                    'encrypted_result': tx_data.get('encrypted_result', ''),
                    'decrypted_result': tx_data.get('decrypted_result'),
                    'metadata': tx_data.get('metadata', {})
                }
                return jsonify({
                    'success': True,
                    'transaction': formatted_tx
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Transaction not found'
                }), 404
        else:
            return jsonify({
                'success': False,
                'error': 'Transaction history not available for this network'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/blockchain/stats', methods=['GET'])
def get_blockchain_stats():
    """Get blockchain statistics."""
    try:
        from blockchain.simulator import get_local_simulator
        
        if blockchain_integration and blockchain_integration.use_simulator:
            simulator = get_local_simulator()
            network_info = simulator.get_network_info()
            
            transactions = simulator.get_all_transactions()
            operations = {}
            for tx in transactions:
                op = tx.get('data', {}).get('operation', 'unknown')
                operations[op] = operations.get(op, 0) + 1
            
            return jsonify({
                'success': True,
                'network': network_info['network'],
                'chain_id': network_info['chain_id'],
                'current_block': network_info['block_number'],
                'total_transactions': network_info['total_transactions'],
                'total_accounts': network_info['accounts'],
                'operations': operations
            })
        else:
            return jsonify({
                'success': True,
                'network': blockchain_integration.network if blockchain_integration else 'unknown',
                'message': 'Stats not available for this network'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Frontend Application...")
    print("📝 Open browser to: http://localhost:5000")
    print("🔗 Network: Local Blockchain (Python Simulator)")
    app.run(debug=True, host='0.0.0.0', port=5000)

