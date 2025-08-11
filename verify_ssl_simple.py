#!/usr/bin/env python3
"""
Simple SSL Verification Script
Verifies that SSL certificates can be loaded without running the full Flask app
"""

import os
import ssl

def verify_ssl_config():
    """Verify SSL configuration"""
    print("Verifying SSL configuration...")
    
    # Get certificate paths from environment or use defaults
    cert_path = os.environ.get('SSL_CERT_PATH', 'config/certificates/smartdispute-canada.me.pem')
    key_path = os.environ.get('SSL_KEY_PATH', 'config/certificates/smartdispute-canada.me.key')
    
    print(f"Certificate path: {cert_path}")
    print(f"Private key path: {key_path}")
    
    # Check if files exist
    if not os.path.exists(cert_path):
        print(f"ERROR: Certificate file not found at {cert_path}")
        return False
        
    if not os.path.exists(key_path):
        print(f"ERROR: Private key file not found at {key_path}")
        return False
    
    # Try to create SSL context
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_path, key_path)
        print("SUCCESS: SSL context created successfully")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create SSL context: {e}")
        return False

if __name__ == "__main__":
    success = verify_ssl_config()
    if success:
        print("\nSSL configuration verified successfully!")
        exit(0)
    else:
        print("\nSSL configuration verification failed!")
        exit(1)