#!/usr/bin/env python3
"""
Script to verify if smartdisputecanada.me is configured correctly
"""

import requests
import json
import socket
import ssl
from datetime import datetime

def check_dns_configuration():
    """Check DNS configuration for both domains"""
    print("DNS Configuration Check")
    print("=" * 50)
    
    domains = ["smartdisputecanada.me", "www.smartdisputecanada.me"]
    
    for domain in domains:
        print(f"\n--- {domain} ---")
        try:
            # Check A records
            response = requests.get(f"https://dns.google/resolve?name={domain}&type=A")
            data = response.json()
            
            if 'Answer' in data:
                print("A Records:")
                for answer in data['Answer']:
                    print(f"  IP: {answer['data']}")
            else:
                print("No A records found")
            
            # Check CNAME records
            response = requests.get(f"https://dns.google/resolve?name={domain}&type=CNAME")
            data = response.json()
            
            if 'Answer' in data:
                print("CNAME Records:")
                for answer in data['Answer']:
                    print(f"  Target: {answer['data']}")
            else:
                print("No CNAME records found")
                
        except Exception as e:
            print(f"Error checking DNS: {str(e)}")

def check_ssl_certificate(domain):
    """Check SSL certificate details"""
    print(f"\nSSL Certificate Check for {domain}")
    print("-" * 40)
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
        print("Certificate Details:")
        print(f"  Issuer: {cert['issuer']}")
        print(f"  Valid From: {cert['notBefore']}")
        print(f"  Valid Until: {cert['notAfter']}")
        
        # Check SANs
        sans = cert.get('subjectAltName', [])
        print(f"  Subject Alternative Names:")
        for san_type, san_value in sans:
            print(f"    {san_value}")
            
        # Check if domain is in SANs
        domain_found = any(san_value == domain for san_type, san_value in sans)
        if domain_found:
            print(f"  Status: SUCCESS - {domain} found in certificate")
        else:
            print(f"  Status: ERROR - {domain} NOT found in certificate")
            
        return True
    except Exception as e:
        print(f"  Status: ERROR - SSL check failed: {str(e)}")
        return False

def check_http_connectivity(domain):
    """Check HTTP/HTTPS connectivity"""
    print(f"\nHTTP Connectivity Check for {domain}")
    print("-" * 40)
    
    try:
        # Test HTTPS
        response = requests.get(f"https://{domain}", timeout=10, allow_redirects=True)
        print(f"  HTTPS Status: {response.status_code}")
        print(f"  Final URL: {response.url}")
        print(f"  Status: SUCCESS")
        return True
    except Exception as e:
        print(f"  HTTPS Status: ERROR - {str(e)}")
        return False

def check_railway_health():
    """Check Railway application health"""
    print("\nRailway Application Health Check")
    print("=" * 50)
    
    try:
        # Try to access the health endpoint
        response = requests.get("https://smartdisputecanada.me/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  Status: {data.get('status', 'Unknown')}")
            print(f"  Timestamp: {data.get('timestamp', 'Unknown')}")
            
            # Check individual components
            checks = data.get('checks', {})
            for component, details in checks.items():
                status = details.get('status', 'unknown')
                message = details.get('message', 'No message')
                print(f"  {component}: {status} - {message}")
        else:
            print(f"  Status: ERROR - HTTP {response.status_code}")
    except Exception as e:
        print(f"  Status: ERROR - {str(e)}")

def check_cloudflare_headers():
    """Check for Cloudflare headers"""
    print("\nCloudflare Configuration Check")
    print("=" * 50)
    
    try:
        response = requests.get("https://smartdisputecanada.me", timeout=10)
        headers = response.headers
        
        cloudflare_headers = [
            'server', 'cf-ray', 'cf-cache-status',
            'cf-request-id', 'expect-ct'
        ]
        
        found_headers = []
        for header in cloudflare_headers:
            if header in headers:
                found_headers.append(f"{header}: {headers[header]}")
        
        if found_headers:
            print("Cloudflare Headers Found:")
            for header in found_headers:
                print(f"  {header}")
        else:
            print("No Cloudflare headers detected")
            
    except Exception as e:
        print(f"Error checking Cloudflare headers: {str(e)}")

def main():
    """Main verification function"""
    print("Smart Dispute Canada Configuration Verification")
    print("=" * 60)
    print(f"Check started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check DNS configuration
    check_dns_configuration()
    
    # Check SSL certificates
    domains = ["smartdisputecanada.me", "www.smartdisputecanada.me"]
    for domain in domains:
        check_ssl_certificate(domain)
    
    # Check HTTP connectivity
    for domain in domains:
        check_http_connectivity(domain)
    
    # Check Railway health
    check_railway_health()
    
    # Check Cloudflare configuration
    check_cloudflare_headers()
    
    print("\n" + "=" * 60)
    print("Configuration verification complete.")
    print("If any errors are shown, please review the DNS and SSL configuration.")

if __name__ == "__main__":
    main()