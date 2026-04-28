"""
Poseidon Commitment Computation
================================

Computes cryptographic commitment using Poseidon hash, matching the
circomlib Poseidon(3) implementation used in range_commit.circom.

SPECIFICATION:
    commitment = Poseidon(x, salt, contextHash)

CIRCUIT COMPATIBILITY:
    This implementation matches circomlib's Poseidon(3) template:
    - 3 inputs (x, salt, contextHash)
    - BN254 scalar field prime
    - alpha = 5 (x^5 S-box)
    - t = 4 (state width = nInputs + 1 capacity element)
    - Full rounds R_F = 8, Partial rounds R_P = 56

SECURITY PROPERTIES:
- Binding: Cannot find x' != x with same commitment
- Hiding: Cannot recover x from commitment (requires salt)
- Collision-resistant: Poseidon is designed for algebraic circuits

THESIS REFERENCE: Chapter 3, Section 3.2.2 - Commitment Scheme
"""

from poseidon import Poseidon as _PoseidonHasher

# BN254 scalar field prime (same as used in circomlib)
_BN254_PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617

# Poseidon(3) parameters matching circomlib's template used in range_commit.circom:
# nInputs=3 → t = nInputs + 1 = 4; alpha=5 (x^5); full=8, partial=56
_POSEIDON_3 = _PoseidonHasher(
    p=_BN254_PRIME,
    security_level=128,
    alpha=5,
    input_rate=3,
    t=4,
    full_round=8,
    partial_round=56,
)


def compute_poseidon_commitment(x: int, salt: int, context_hash: int) -> int:
    """
    Compute Poseidon commitment matching circomlib's Poseidon(3) circuit.

    Computes: commitment = Poseidon(x, salt, contextHash)

    The hash function parameters target circomlib Poseidon(3) (BN254, alpha=5,
    t=4, R_F=8, R_P=56).  All inputs are reduced modulo the BN254 scalar field
    prime before hashing to satisfy the field-element constraint.

    Args:
        x: Secret value (private input)
        salt: Random salt (private input, any non-negative integer)
        context_hash: Context binding hash (public input)

    Returns:
        Commitment as BN254 field element (integer in [0, BN254_PRIME))
    """
    # Reduce all inputs into the BN254 scalar field before hashing.
    # In particular, salt generated from os.urandom(32) can exceed the
    # ~254-bit field prime; without reduction the Poseidon library raises
    # a GF bounds error.
    x_f = int(x) % _BN254_PRIME
    salt_f = int(salt) % _BN254_PRIME
    ctx_f = int(context_hash) % _BN254_PRIME

    commitment = _POSEIDON_3.run_hash([x_f, salt_f, ctx_f])
    return int(commitment) % _BN254_PRIME


def verify_commitment(
    x: int,
    salt: int,
    context_hash: int,
    claimed_commitment: int
) -> bool:
    """
    Verify a commitment matches the inputs.

    Args:
        x: Secret value
        salt: Salt used in commitment
        context_hash: Context hash
        claimed_commitment: Commitment to verify

    Returns:
        True if commitment is valid
    """
    computed_commitment = compute_poseidon_commitment(x, salt, context_hash)
    return computed_commitment == claimed_commitment


# Example usage
if __name__ == "__main__":
    print("Poseidon Commitment - Test\n")

    # Example parameters
    x = 500000          # Secret value
    salt = 12345678901234567890  # Random salt
    context_hash = 99999999999999999999  # From context_hasher

    # Compute commitment
    commitment = compute_poseidon_commitment(x, salt, context_hash)

    print(f"Inputs:")
    print(f"  x (secret): [REDACTED]")
    print(f"  salt (secret): [REDACTED]")
    print(f"  contextHash: {hex(context_hash)}")
    print(f"\nCommitment: {hex(commitment)}")

    # Verify commitment
    is_valid = verify_commitment(x, salt, context_hash, commitment)
    print(f"Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")


