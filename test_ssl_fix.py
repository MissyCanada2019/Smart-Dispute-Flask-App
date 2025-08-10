#!/usr/bin/env python3
"""
Script to test SSL connectivity after fixes have been applied
"""

import socket
import ssl
import http.client

def test_ssl_certificate(domain):
    """Test SSL certificate for a domain"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
        print(f"SUCCESS SSL certificate for {domain}:")
        print(f"  Issuer: {cert['issuer']}")
        print(f"  Valid From: {cert['notBefore']}")
        print(f"  Valid Until: {cert['notAfter']}")
        print(f"  SANs: {cert.get('subjectAltName', [])}")
        
        # Check if www domain is in SANs
        sans = cert.get('subjectAltName', [])
        for san_type, san_value in sans:
            if san_value == domain:
                print(f"  CONFIRMED: {domain} is included in certificate")
                return True
        
        print(f"  WARNING: {domain} not found in certificate SANs")
        return False
    except Exception as e:
        print(f"ERROR SSL certificate check failed for {domain}: {str(e)}")
        return False

def test_https_connectivity(domain):
    """Test HTTPS connectivity"""
    try:
        conn = http.client.HTTPSConnection(domain, timeout=10)
        conn.request("GET", "/")
        response = conn.getresponse()
        print(f"SUCCESS HTTPS connectivity to {domain}:")
        print(f"  Status Code: {response.status}")
        print(f"  Server: {response.getheader('Server', 'Unknown')}")
        return True
    except Exception as e:
        print(f"ERROR HTTPS connection failed for {domain}: {str(e)}")
        return False

def main():
    """Main function to test SSL connectivity"""
    print("Testing SSL connectivity after fixes...")
    print("=" * 50)
    
    domains = ["smartdisputecanada.me", "www.smartdisputecanada.me"]
    
    all_tests_passed = True
    
    for domain in domains:
        print(f"\nTesting {domain}...")
        
        # Test SSL certificate
        cert_ok = test_ssl_certificate(domain)
        
        # Test HTTPS connectivity
        https_ok = test_https_connectivity(domain)
        
        if not cert_ok or not https_ok:
            all_tests_passed = False
            print(f"FAIL {domain} has issues")
        else:
            print(f"PASS {domain} is working correctly")
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("SUCCESS All SSL tests passed! The www subdomain issue has been fixed.")
    else:
        print("FAIL Some SSL tests failed. The issue may not be completely resolved yet.")
        print("Please wait a few more minutes for DNS and certificate propagation.")

if __name__ == "__main__":
    main()