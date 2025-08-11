#!/usr/bin/env python3
"""
SSL Configuration Test Script
Tests the SSL certificate configuration for the Smart Dispute Canada application
"""

import os
import ssl

def check_certificate_files():
    """Check if certificate files exist and are readable"""
    cert_path = os.environ.get('SSL_CERT_PATH', 'config/certificates/smartdispute-canada.me.pem')
    key_path = os.environ.get('SSL_KEY_PATH', 'config/certificates/smartdispute-canada.me.key')
    
    print("Checking SSL certificate files...")
    
    # Check certificate file
    if os.path.exists(cert_path):
        print(f"OK Certificate file found: {cert_path}")
        try:
            with open(cert_path, 'r') as f:
                content = f.read()
                if "BEGIN CERTIFICATE" in content:
                    print("OK Certificate file format verified")
                else:
                    print("ERROR Certificate file format invalid")
                    return False
        except Exception as e:
            print(f"ERROR Error reading certificate file: {e}")
            return False
    else:
        print(f"ERROR Certificate file not found: {cert_path}")
        return False
    
    # Check key file
    if os.path.exists(key_path):
        print(f"OK Private key file found: {key_path}")
        try:
            with open(key_path, 'r') as f:
                content = f.read()
                if "BEGIN PRIVATE KEY" in content or "BEGIN RSA PRIVATE KEY" in content:
                    print("OK Private key file format verified")
                else:
                    print("ERROR Private key file format invalid")
                    return False
        except Exception as e:
            print(f"ERROR Error reading private key file: {e}")
            return False
    else:
        print(f"ERROR Private key file not found: {key_path}")
        return False
    
    return True

def test_ssl_context():
    """Test creating SSL context with the certificates"""
    cert_path = os.environ.get('SSL_CERT_PATH', 'config/certificates/smartdispute-canada.me.pem')
    key_path = os.environ.get('SSL_KEY_PATH', 'config/certificates/smartdispute-canada.me.key')
    
    try:
        # Create SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_path, key_path)
        print("OK SSL context created successfully with provided certificates")
        return True
    except Exception as e:
        print(f"ERROR Error creating SSL context: {e}")
        return False

def main():
    """Main test function"""
    print("SSL Configuration Test")
    print("=" * 30)
    
    # Run tests
    file_check = check_certificate_files()
    context_check = test_ssl_context()
    
    if file_check and context_check:
        print("\nSUCCESS All SSL configuration tests passed!")
        return True
    else:
        print("\nFAILURE SSL configuration test failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)