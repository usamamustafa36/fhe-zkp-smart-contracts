"""
Witness Sanitizer - Prevent Witness Data Leakage
=================================================

Ensures no witness data (x, salt) leaks through:
- Error messages
- Logs
- Exception stack traces
- Debug output

SECURITY CRITICAL:
This module is essential for maintaining zero-knowledge property.

THESIS REFERENCE: Chapter 3, Section 3.3 - Witness Protection
"""

import re
from typing import Set


# Sensitive keywords that should never appear in logs
SENSITIVE_KEYWORDS = {
    'witness',
    'private input',
    'secret value',
    'salt'
}

# Patterns to redact from error messages
REDACTION_PATTERNS = [
    # JSON with numeric values (must come before general number pattern)
    (r'"x"\s*:\s*"\d+"', '"x": "[REDACTED]"'),
    (r'"salt"\s*:\s*"\d+"', '"salt": "[REDACTED]"'),
    
    # Witness values in error messages (x= or salt= patterns)
    (r'x\s*=\s*\d+', 'x=[REDACTED]'),
    (r'salt\s*=\s*\d+', 'salt=[REDACTED]'),
    
    # Large numbers (field elements, likely witness data)
    (r'\b\d{10,}\b', '[REDACTED_NUMBER]'),
    
    # Hex values (commitments, hashes - could reveal witness)
    (r'0x[0-9a-fA-F]{16,}', '[REDACTED_HEX]'),
    
    # File paths that might contain witness data
    (r'/tmp/\S+witness\S*', '[REDACTED_FILE]'),
]


def sanitize_error(error_message: str) -> str:
    """
    Remove witness data from error messages.
    
    Args:
        error_message: Original error message
    
    Returns:
        Sanitized error message with witness data redacted
    
    Example:
        Input:  "Invalid witness: x=500000, salt=12345..."
        Output: "Invalid witness: x=[REDACTED], salt=[REDACTED]..."
    """
    sanitized = error_message
    
    # Apply all redaction patterns
    for pattern, replacement in REDACTION_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized)
    
    return sanitized


def check_for_leaks(text: str) -> Set[str]:
    """
    Check text for potential witness leaks.
    
    Args:
        text: Text to check (log message, error, etc.)
    
    Returns:
        Set of detected sensitive keywords
    
    Use for testing/auditing:
        leaks = check_for_leaks(log_message)
        if leaks:
            raise SecurityError(f"Witness leak detected: {leaks}")
    """
    text_lower = text.lower()
    detected = set()
    
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in text_lower:
            detected.add(keyword)
    
    return detected


def audit_source_file(file_path: str) -> bool:
    """
    Audit source file for potential witness leaks.
    
    Args:
        file_path: Path to Python file to audit
    
    Returns:
        True if no leaks detected, False otherwise
    
    Checks for:
    - print() statements with witness variables
    - logger.info/debug with witness data
    - Unprotected file writes
    """
    with open(file_path, 'r') as f:
        source = f.read()
    
    # Check for dangerous patterns
    dangerous_patterns = [
        r'print\s*\(\s*["\']?\s*x\s*["\']?\s*\)',  # print(x)
        r'print\s*\(\s*["\']?\s*salt\s*["\']?\s*\)',  # print(salt)
        r'logger\.\w+\([^)]*\bx\b[^)]*\)',  # logger.info(...x...)
        r'logger\.\w+\([^)]*\bsalt\b[^)]*\)',  # logger.info(...salt...)
        r'open\([^)]*witness[^)]*,\s*["\']w["\']',  # open(...witness..., 'w')
    ]
    
    violations = []
    for pattern in dangerous_patterns:
        matches = re.findall(pattern, source, re.IGNORECASE)
        if matches:
            violations.extend(matches)
    
    if violations:
        print(f"⚠️  Potential witness leaks in {file_path}:")
        for v in violations:
            print(f"   - {v}")
        return False
    
    return True


# Example usage
if __name__ == "__main__":
    print("Witness Sanitizer - Test\n")
    
    # Test error sanitization
    test_errors = [
        "Invalid witness: x=500000, salt=123456789",
        "Proof failed with value 0x123456789abcdef0",
        "File error: /tmp/witness_12345.json",
        '{"x": "500000", "salt": "123456789"}',
    ]
    
    print("Error Sanitization:")
    for error in test_errors:
        sanitized = sanitize_error(error)
        print(f"  Original:  {error}")
        print(f"  Sanitized: {sanitized}")
        print()
    
    # Test leak detection
    test_logs = [
        "Processing computation",  # Safe
        "Witness value is 500000",  # Unsafe!
        "Computing private input hash",  # Unsafe!
    ]
    
    print("\nLeak Detection:")
    for log in test_logs:
        leaks = check_for_leaks(log)
        status = "❌ LEAK" if leaks else "✅ Safe"
        print(f"  {status}: {log}")
        if leaks:
            print(f"    Detected: {leaks}")
