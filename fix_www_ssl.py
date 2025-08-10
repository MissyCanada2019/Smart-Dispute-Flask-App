#!/usr/bin/env python3
"""
Script to fix SSL certificate issues for www.smartdisputecanada.me subdomain

This script provides guidance on how to fix SSL certificate issues for the www subdomain
by ensuring proper certificate coverage and Cloudflare configuration.
"""

import socket
import ssl
import http.client
import json
import os
import sys

def check_ssl_certificate(domain):
    """Check SSL certificate details using standard libraries"""
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
        return cert
    except Exception as e:
        print(f"ERROR SSL certificate check failed for {domain}: {str(e)}")
        return None

def check_https_connectivity(domain):
    """Check HTTPS connectivity using http.client"""
    try:
        conn = http.client.HTTPSConnection(domain, timeout=5)
        conn.request("HEAD", "/")
        response = conn.getresponse()
        print(f"SUCCESS HTTPS connectivity to {domain}:")
        print(f"  Status Code: {response.status}")
        print(f"  Server: {response.getheader('Server', 'Unknown')}")
        return True
    except Exception as e:
        print(f"ERROR HTTPS connection failed for {domain}: {str(e)}")
        return False

def diagnose_ssl_issue():
    """Diagnose the SSL issue for both main domain and www subdomain"""
    print("Diagnosing SSL certificate issues...")
    print("=" * 50)
    
    # Check main domain certificate
    main_domain = "smartdisputecanada.me"
    www_domain = "www.smartdisputecanada.me"
    
    print(f"\nChecking main domain: {main_domain}")
    main_cert = check_ssl_certificate(main_domain)
    
    # Test HTTPS connectivity for main domain
    check_https_connectivity(main_domain)
    
    print(f"\nChecking www subdomain: {www_domain}")
    www_cert = check_ssl_certificate(www_domain)
    
    # Test HTTPS connectivity for www subdomain
    check_https_connectivity(www_domain)
    
    return main_cert, www_cert

def generate_fix_instructions():
    """Generate instructions to fix the SSL certificate issue"""
    print("\nFix Instructions for www.smartdisputecanada.me SSL Issue")
    print("=" * 60)
    
    print("""
Issue Identified:
The SSL certificate for smartdisputecanada.me does not include www.smartdisputecanada.me 
as a Subject Alternative Name (SAN), causing SSL handshake failures when accessing the www subdomain.

Solution Options:
""")
    
    print("1. Railway Automatic SSL Certificate Update:")
    print("   - Go to Railway Dashboard -> Your Project -> Settings -> Domains")
    print("   - Remove and re-add the www.smartdisputecanada.me domain")
    print("   - Railway should automatically provision a new certificate that includes both domains")
    print("   - Wait 5-15 minutes for the certificate to be issued")
    
    print("\n2. Manual Cloudflare Configuration:")
    print("   - Log in to Cloudflare Dashboard")
    print("   - Go to SSL/TLS -> Edge Certificates")
    print("   - Click 'Delete' to remove current certificate (if needed)")
    print("   - Go to SSL/TLS -> Origin Server")
    print("   - Click 'Reinstall Certificate' to get a new certificate that includes www subdomain")
    
    print("\n3. Cloudflare DNS Record Update:")
    print("   - Log in to Cloudflare Dashboard")
    print("   - Go to DNS -> Records")
    print("   - Find the www record and ensure it's properly configured:")
    print("     Type: CNAME")
    print("     Name: www")
    print("     Content: smartdisputecanada.me or your Railway app URL")
    print("     Proxy status: Proxied (orange cloud enabled)")
    
    print("\n4. Force SSL Certificate Revalidation:")
    print("   - In Cloudflare, go to SSL/TLS -> Edge Certificates")
    print("   - Set 'Always Use HTTPS' to 'On'")
    print("   - Set 'Opportunistic Encryption' to 'On'")
    print("   - Set 'TLS 1.3' to 'On'")
    
    print("\n5. Verify Configuration:")
    print("   After making changes, wait 5-10 minutes and run:")
    print("   python check_smartdispute_ssl.py")
    
    print("\nImportant Notes:")
    print("   - DNS changes may take up to 24 hours to propagate globally")
    print("   - SSL certificate provisioning can take 5-30 minutes")
    print("   - Ensure both domains are added to Railway if using Railway for SSL")

def main():
    """Main function to diagnose and provide fix instructions"""
    print("Smart Dispute Canada SSL Fix Tool")
    print("=================================")
    
    # Diagnose the current SSL issue
    main_cert, www_cert = diagnose_ssl_issue()
    
    # Generate fix instructions
    generate_fix_instructions()
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Follow the instructions above to fix the SSL certificate issue")
    print("2. Wait for DNS propagation and certificate provisioning")
    print("3. Run this script again to verify the fix")
    print("4. Test both https://smartdisputecanada.me and https://www.smartdisputecanada.me")

if __name__ == "__main__":
    main()