"""
Context Hash Computation
=========================

Computes deterministic context hash for anti-replay protection.

SPECIFICATION:
    contextHash = Poseidon(chainId, contractAddr, opType, requestId)

SECURITY:
- Context binding prevents:
  * Cross-chain replay (chainId)
  * Cross-contract replay (contractAddr)
  * Operation confusion (opType)
  * Same-context replay (requestId - must be unique)

THESIS REFERENCE: Chapter 3, Section 3.2.3 - Context Binding
"""

from typing import Optional
import hashlib


def compute_context_hash(
    chain_id: int,
    contract_address: bytes,
    operation_type: int,
    request_id: bytes
) -> int:
    """
    Compute context hash for ZKP commitment binding.
    
    Args:
        chain_id: Blockchain chain ID (uint256)
                  Examples: 1 (mainnet), 11155111 (Sepolia)
        contract_address: Contract address (20 bytes)
        operation_type: Operation code (uint8)
                        0 = validate, 1 = compute, 2 = decrypt
        request_id: Unique request identifier (32 bytes)
                    Typically: keccak256(timestamp || sender)
    
    Returns:
        Field element (integer) suitable for SNARK circuit
    
    Implementation:
        Currently uses keccak256 for compatibility.
        TODO: Replace with Poseidon hash for circuit efficiency.
    
    Security Properties:
        - Deterministic: Same inputs → same hash
        - Collision-resistant: Hard to find hash collisions
        - One-way: Cannot reverse to inputs
    """
    
    # Validate inputs
    if not (0 <= chain_id < 2**256):
        raise ValueError(f"Invalid chain_id: {chain_id}")
    
    if len(contract_address) != 20:
        raise ValueError(f"Invalid contract_address length: {len(contract_address)}")
    
    if not (0 <= operation_type < 256):
        raise ValueError(f"Invalid operation_type: {operation_type}")
    
    if len(request_id) != 32:
        raise ValueError(f"Invalid request_id length: {len(request_id)}")
    
    # Encode parameters
    # Format: chainId (32 bytes) || contractAddr (20 bytes) || opType (1 byte) || requestId (32 bytes)
    chain_id_bytes = chain_id.to_bytes(32, 'big')
    op_type_bytes = operation_type.to_bytes(1, 'big')
    
    # Concatenate all fields
    data = chain_id_bytes + contract_address + op_type_bytes + request_id
    
    # Hash with keccak256
    context_hash_bytes = hashlib.sha3_256(data).digest()
    
    # Convert to field element
    context_hash = int.from_bytes(context_hash_bytes, 'big')
    
    # Reduce modulo BN254 scalar field (for SNARK compatibility)
    BN254_SCALAR_FIELD = 21888242871839275222246405745257275088548364400416034343698204186575808495617
    context_hash = context_hash % BN254_SCALAR_FIELD
    
    return context_hash


def generate_request_id(timestamp: Optional[int] = None, sender: Optional[bytes] = None) -> bytes:
    """
    Generate unique request ID for context binding.
    
    Args:
        timestamp: Unix timestamp (optional, uses current time if None)
        sender: Sender address (optional, uses zero address if None)
    
    Returns:
        32-byte unique request ID
    
    Example:
        request_id = generate_request_id(1704990000, sender_address)
    """
    import time
    
    if timestamp is None:
        timestamp = int(time.time())
    
    if sender is None:
        sender = b'\x00' * 20
    elif len(sender) != 20:
        raise ValueError(f"Sender must be 20 bytes, got {len(sender)}")
    
    # Hash timestamp + sender for uniqueness
    data = timestamp.to_bytes(8, 'big') + sender
    request_id = hashlib.sha3_256(data).digest()
    
    return request_id


# Example usage
if __name__ == "__main__":
    print("Context Hash Computation - Test\n")
    
    # Example parameters
    chain_id = 11155111  # Sepolia testnet
    contract_address = bytes.fromhex("0000000000000000000000000000000000000001")
    operation_type = 0  # validate
    request_id = generate_request_id(1704990000, b'\x00' * 20)
    
    # Compute context hash
    context_hash = compute_context_hash(
        chain_id, contract_address, operation_type, request_id
    )
    
    print(f"Inputs:")
    print(f"  Chain ID: {chain_id}")
    print(f"  Contract: 0x{contract_address.hex()}")
    print(f"  Operation: {operation_type}")
    print(f"  Request ID: 0x{request_id.hex()[:16]}...")
    print(f"\nContext Hash: {hex(context_hash)}")
    print(f"Field Element: {context_hash}")
