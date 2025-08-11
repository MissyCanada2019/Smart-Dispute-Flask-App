#!/usr/bin/env python3
"""
Script to verify that the SSL certificate issue for smartdisputecanada.me has been resolved
"""

import socket
import ssl
import http.client
import sys
import time

def check_ssl_certificate(domain):
    """Check SSL certificate details using standard libraries"""
    try:
        print(f"Checking SSL certificate for {domain}...")
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
        print(f"✓ SSL certificate for {domain}:")
        print(f"  Issuer: {cert['issuer']}")
        print(f"  Valid From: {cert['notBefore']}")
        print(f"  Valid Until: {cert['notAfter']}")
        print(f"  SANs: {cert.get('subjectAltName', [])}")
        
        # Check expiration
        import datetime
        exp_date = datetime.datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
        days_until_expiry = (exp_date - datetime.datetime.utcnow()).days
        
        if days_until_expiry < 0:
            print(f"  ⚠ Certificate expired {abs(days_until_expiry)} days ago")
            return False
        elif days_until_expiry < 14:
            print(f"  ⚠ Certificate expires in {days_until_expiry} days")
            return False
        else:
            print(f"  ✓ Certificate valid for {days_until_expiry} more days")
            return True
            
    except Exception as e:
        print(f"✗ SSL certificate check failed for {domain}: {str(e)}")
        return False

def check_https_connectivity(domain):
    """Check HTTPS connectivity using http.client"""
    try:
        print(f"Checking HTTPS connectivity to {domain}...")
        conn = http.client.HTTPSConnection(domain, timeout=10)
        conn.request("HEAD", "/")
        response = conn.getresponse()
        print(f"✓ HTTPS connectivity to {domain}:")
        print(f"  Status Code: {response.status}")
        print(f"  Server: {response.getheader('Server', 'Unknown')}")
        return response.status == 200 or (300 <= response.status < 400)
    except Exception as e:
        print(f"✗ HTTPS connection failed for {domain}: {str(e)}")
        return False

def check_domain_resolves(domain):
    """Check if domain resolves to an IP address"""
    try:
        print(f"Checking DNS resolution for {domain}...")
        ip = socket.gethostbyname(domain)
        print(f"✓ {domain} resolves to {ip}")
        return True
    except Exception as e:
        print(f"✗ DNS resolution failed for {domain}: {str(e)}")
        return False

def main():
    """Main function to verify SSL fix"""
    print("SSL Fix Verification for Smart Dispute Canada")
    print("=" * 50)
    
    domains = ["smartdisputecanada.me", "www.smartdisputecanada.me"]
    all_passed = True
    
    for domain in domains:
        print(f"\n--- Testing {domain} ---")
        
        # Check DNS resolution
        if not check_domain_resolves(domain):
            all_passed = False
            continue
            
        # Check SSL certificate
        ssl_ok = check_ssl_certificate(domain)
        if not ssl_ok:
            all_passed = False
            
        # Check HTTPS connectivity
        https_ok = check_https_connectivity(domain)
        if not https_ok:
            all_passed = False
            
        if ssl_ok and https_ok:
            print(f"✓ {domain} - All checks passed")
        else:
            print(f"✗ {domain} - Some checks failed")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All SSL checks passed! The issue appears to be resolved.")
        print("✓ Both domains are accessible over HTTPS with valid certificates.")
    else:
        print("✗ Some SSL checks failed. The issue may not be fully resolved.")
        print("✗ Please review the error messages above and check your configuration.")
        
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)