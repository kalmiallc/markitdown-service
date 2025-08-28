#!/usr/bin/env python3
"""
Test script for SSRF protection validation - Uses security module
"""
import sys

# Import from the security module
from security import validate_url_security

def test_ssrf_protection():
    """Test various SSRF attack vectors"""
    
    test_cases = [
        # Valid URLs (should pass)
        ("https://www.google.com", True),
        ("http://example.com", True),
        ("https://github.com/microsoft/markitdown", True),
        ("http://httpbin.org/get", True),
        
        # Invalid schemes (should fail)
        ("ftp://example.com", False),
        ("file:///etc/passwd", False),
        ("gopher://example.com", False),
        
        # Localhost variations (should fail)
        ("http://localhost", False),
        ("http://127.0.0.1", False),
        ("http://0.0.0.0", False),
        ("http://::1", False),
        ("https://localhost:8080", False),
        
        # Private networks (should fail)
        ("http://192.168.1.1", False),
        ("http://10.0.0.1", False),
        ("http://172.16.0.1", False),
        
        # Cloud metadata endpoints (should fail)
        ("http://169.254.169.254", False),
        ("http://metadata.google.internal", False),
        ("http://metadata.azure.com", False),
        
        # Link-local (should fail)
        ("http://169.254.1.1", False),
        
        # Invalid ports (should fail)
        ("http://example.com:22", False),
        ("http://example.com:3389", False),
        ("http://example.com:5432", False),
        
        # Valid ports (should pass)
        ("http://example.com:80", True),
        ("https://example.com:443", True),
        ("http://example.com:8080", True),
        ("https://example.com:8443", True),
        
        # Suspicious patterns (should fail)
        ("http://internal.company.com", False),
        ("http://metadata.example.com", False),
        
        # Edge cases
        ("http://", False),  # Invalid URL
        ("", False),         # Empty URL
    ]
    
    print("Testing SSRF Protection...")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for url, should_pass in test_cases:
        is_valid, message = validate_url_security(url)
        
        if is_valid == should_pass:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1
        
        expected = "ALLOW" if should_pass else "BLOCK"
        actual = "ALLOWED" if is_valid else "BLOCKED"
        
        print(f"{status} | {expected:5} | {actual:7} | {url}")
        if not is_valid and message:
            print(f"      Reason: {message}")
        print()
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("❌ Some tests failed!")
        return False
    else:
        print("✅ All tests passed!")
        return True

if __name__ == "__main__":
    success = test_ssrf_protection()
    sys.exit(0 if success else 1)