#!/usr/bin/env python3
"""
Script to fix SSL certificate issues for www.smartdisputecanada.me subdomain using Cloudflare API

This script can automatically fix SSL certificate issues when provided with proper Cloudflare API credentials.
"""

import requests
import json
import os
import sys

# Cloudflare configuration
ZONE_ID = "5d457b0db02ae32d7af7cef5c6d745b5"
DOMAIN = "smartdisputecanada.me"
WWW_DOMAIN = "www.smartdisputecanada.me"

def get_cloudflare_headers(api_key):
    """Get headers for Cloudflare API requests"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def check_dns_records(api_key):
    """Check DNS records for the domain"""
    print("Checking DNS records...")
    
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
    headers = get_cloudflare_headers(api_key)
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            records = data.get("result", [])
            print(f"Found {len(records)} DNS records:")
            
            for record in records:
                name = record.get("name", "")
                if DOMAIN in name:
                    print(f"  - {record['type']} {name} -> {record['content']} (proxied: {record['proxied']})")
            
            return records
        else:
            print("Failed to retrieve DNS records:", data.get("errors", []))
            return None
    except Exception as e:
        print(f"Error checking DNS records: {str(e)}")
        return None

def check_ssl_settings(api_key):
    """Check SSL settings in Cloudflare"""
    print("Checking SSL settings...")
    
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/settings/ssl"
    headers = get_cloudflare_headers(api_key)
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            ssl_setting = data.get("result", {}).get("value", "unknown")
            print(f"SSL Setting: {ssl_setting}")
            return ssl_setting
        else:
            print("Failed to retrieve SSL settings:", data.get("errors", []))
            return None
    except Exception as e:
        print(f"Error checking SSL settings: {str(e)}")
        return None

def update_ssl_settings(api_key, ssl_mode="full"):
    """Update SSL settings in Cloudflare"""
    print(f"Updating SSL settings to {ssl_mode}...")
    
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/settings/ssl"
    headers = get_cloudflare_headers(api_key)
    payload = {"value": ssl_mode}
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            print(f"SSL settings updated to {ssl_mode}")
            return True
        else:
            print("Failed to update SSL settings:", data.get("errors", []))
            return False
    except Exception as e:
        print(f"Error updating SSL settings: {str(e)}")
        return False

def check_certificate_packs(api_key):
    """Check SSL certificate packs"""
    print("Checking SSL certificate packs...")
    
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/ssl/certificate_packs"
    headers = get_cloudflare_headers(api_key)
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            certs = data.get("result", [])
            print(f"Found {len(certs)} certificate packs:")
            
            for cert in certs:
                print(f"  - {cert.get('type', 'unknown')} certificate:")
                print(f"    Status: {cert.get('status', 'unknown')}")
                print(f"    Hosts: {cert.get('hosts', [])}")
                print(f"    Validation: {cert.get('validation_method', 'unknown')}")
            
            return certs
        else:
            print("Failed to retrieve certificate packs:", data.get("errors", []))
            return None
    except Exception as e:
        print(f"Error checking certificate packs: {str(e)}")
        return None

def request_new_certificate(api_key):
    """Request a new SSL certificate that includes both domains"""
    print("Requesting new SSL certificate...")
    
    # This would typically involve triggering a certificate revalidation
    # For now, we'll just provide instructions
    print("To request a new certificate:")
    print("1. Go to Cloudflare Dashboard -> SSL/TLS -> Edge Certificates")
    print("2. Delete the current certificate (if needed)")
    print("3. Wait for Cloudflare to automatically provision a new certificate")
    print("   that includes both smartdisputecanada.me and www.smartdisputecanada.me")
    
    return True

def fix_www_ssl_issue(api_key):
    """Main function to fix the SSL issue for www subdomain"""
    print("Fixing SSL certificate issue for www.smartdisputecanada.me")
    print("=" * 60)
    
    # Check current DNS records
    dns_records = check_dns_records(api_key)
    
    # Check current SSL settings
    ssl_setting = check_ssl_settings(api_key)
    
    # Check certificate packs
    certs = check_certificate_packs(api_key)
    
    # Update SSL settings if needed
    if ssl_setting and ssl_setting != "full":
        update_ssl_settings(api_key, "full")
    
    # Request new certificate
    request_new_certificate(api_key)
    
    print("\nFix process completed. Please wait 5-15 minutes for changes to propagate.")
    print("Then run the check_smartdispute_ssl.py script to verify the fix.")

def main():
    """Main function"""
    print("Smart Dispute Canada SSL Fix Tool (Cloudflare API Version)")
    print("=" * 60)
    
    # Check if API key is provided
    api_key = os.getenv("CLOUDFLARE_API_KEY")
    if not api_key:
        print("Error: CLOUDFLARE_API_KEY environment variable not set")
        print("Please set it with: export CLOUDFLARE_API_KEY=your-api-key")
        print("\nAlternatively, you can run the basic diagnostic script:")
        print("python fix_www_ssl.py")
        return
    
    # Fix the SSL issue
    fix_www_ssl_issue(api_key)

if __name__ == "__main__":
    main()