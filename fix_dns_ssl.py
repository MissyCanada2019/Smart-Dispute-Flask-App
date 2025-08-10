#!/usr/bin/env python3
"""
Script to diagnose and fix DNS and SSL issues for smartdisputecanada.me
"""

import requests
import json
import socket
import ssl

def check_dns_records(domain):
    """Check DNS records using Google DNS API"""
    print(f"Checking DNS records for {domain}...")
    
    try:
        # Check A records
        response = requests.get(f"https://dns.google/resolve?name={domain}&type=A")
        data = response.json()
        
        if 'Answer' in data:
            print("A Records:")
            for answer in data['Answer']:
                print(f"  {answer['data']}")
        else:
            print("No A records found")
        
        # Check CNAME records
        response = requests.get(f"https://dns.google/resolve?name={domain}&type=CNAME")
        data = response.json()
        
        if 'Answer' in data:
            print("CNAME Records:")
            for answer in data['Answer']:
                print(f"  {answer['data']}")
        else:
            print("No CNAME records found")
            
    except Exception as e:
        print(f"Error checking DNS records: {str(e)}")

def check_ssl_certificate(domain):
    """Check SSL certificate for domain"""
    print(f"Checking SSL certificate for {domain}...")
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
        print("SSL Certificate Details:")
        print(f"  Issuer: {cert['issuer']}")
        print(f"  Valid From: {cert['notBefore']}")
        print(f"  Valid Until: {cert['notAfter']}")
        print(f"  SANs: {cert.get('subjectAltName', [])}")
        
        # Check if domain is in SANs
        sans = cert.get('subjectAltName', [])
        domain_found = False
        for san_type, san_value in sans:
            if san_value == domain:
                domain_found = True
                break
                
        if domain_found:
            print(f"  SUCCESS {domain} found in certificate")
        else:
            print(f"  ERROR {domain} NOT found in certificate")
            
        return True
    except Exception as e:
        print(f"  ERROR SSL certificate check failed: {str(e)}")
        return False

def get_railway_domains():
    """Get Railway domain configuration instructions"""
    print("Railway Domain Configuration:")
    print("=" * 40)
    print("1. Log in to Railway Dashboard (https://railway.app)")
    print("2. Go to your Smart Dispute Canada project")
    print("3. Click Settings → Domains")
    print("4. Add these domains:")
    print("   - smartdisputecanada.me")
    print("   - www.smartdisputecanada.me")
    print("5. Railway will provide DNS records to configure")

def get_cloudflare_dns_config():
    """Get Cloudflare DNS configuration instructions"""
    print("\nCloudflare DNS Configuration:")
    print("=" * 40)
    print("In Cloudflare Dashboard:")
    print("1. Go to DNS section")
    print("2. Add these records:")
    print("\n   # Root domain CNAME")
    print("   Type: CNAME")
    print("   Name: @")
    print("   Value: [your-railway-app].railway.app")
    print("   Proxy: Enabled (orange cloud)")
    print("\n   # WWW subdomain CNAME")
    print("   Type: CNAME")
    print("   Name: www")
    print("   Value: smartdisputecanada.me")
    print("   Proxy: Enabled (orange cloud)")

def get_ssl_fix_instructions():
    """Get SSL fix instructions"""
    print("\nSSL Fix Instructions:")
    print("=" * 40)
    print("1. In Railway Dashboard:")
    print("   - Remove both domains")
    print("   - Wait 1 minute")
    print("   - Re-add both domains")
    print("2. In Cloudflare Dashboard:")
    print("   - SSL/TLS → Overview")
    print("   - Set encryption mode to 'Full'")
    print("   - Enable 'Always Use HTTPS'")
    print("3. Wait 5-15 minutes for certificate provisioning")

def main():
    """Main function to diagnose and fix DNS/SSL issues"""
    print("Smart Dispute Canada DNS/SSL Fix Tool")
    print("=" * 50)
    
    domains = ["smartdisputecanada.me", "www.smartdisputecanada.me"]
    
    for domain in domains:
        print(f"\n--- {domain} ---")
        check_dns_records(domain)
        print()
        check_ssl_certificate(domain)
    
    print("\n" + "=" * 50)
    get_railway_domains()
    get_cloudflare_dns_config()
    get_ssl_fix_instructions()
    
    print("\nAfter making changes, wait 5-10 minutes and run this script again to verify.")

if __name__ == "__main__":
    main()