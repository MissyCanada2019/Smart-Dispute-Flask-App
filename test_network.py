#!/usr/bin/env python3
"""
Test script to verify IPv4 and IPv6 connectivity for the Smart Dispute Flask app
"""

import socket
import subprocess
import sys
import time
import threading
import requests
from main import create_app

def test_ipv6_support():
    """Test if the system supports IPv6"""
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.close()
        return True
    except OSError:
        return False

def test_bind_ipv6():
    """Test if we can bind to IPv6"""
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.bind(('::', 0))  # Bind to all IPv6 interfaces
        sock.close()
        return True
    except OSError:
        return False

def test_bind_ipv4():
    """Test if we can bind to IPv4"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 0))  # Bind to all IPv4 interfaces
        sock.close()
        return True
    except OSError:
        return False

def start_flask_test_server():
    """Start the Flask test server in a separate thread"""
    app = create_app()
    
    # Run the app in a separate thread
    def run_app():
        from werkzeug.serving import run_simple
        run_simple('::', 8080, app, use_reloader=False, use_debugger=False)
    
    thread = threading.Thread(target=run_app)
    thread.daemon = True
    thread.start()
    time.sleep(2)  # Give the server time to start
    return thread

def test_http_connectivity():
    """Test HTTP connectivity over both IPv4 and IPv6"""
    results = {}
    
    # Test IPv4 connectivity
    try:
        response = requests.get('http://127.0.0.1:8080/health', timeout=5)
        results['ipv4'] = response.status_code == 200
    except Exception as e:
        results['ipv4'] = False
        results['ipv4_error'] = str(e)
    
    # Test IPv6 connectivity (only if system supports IPv6)
    if test_ipv6_support():
        try:
            response = requests.get('http://[::1]:8080/health', timeout=5)
            results['ipv6'] = response.status_code == 200
        except Exception as e:
            results['ipv6'] = False
            results['ipv6_error'] = str(e)
    else:
        results['ipv6'] = False
        results['ipv6_error'] = "System does not support IPv6"
    
    return results

def main():
    print("🔍 Testing IPv4/IPv6 support for Smart Dispute Flask App")
    print("=" * 60)
    
    # Test system IPv6 support
    ipv6_supported = test_ipv6_support()
    print("🔧 System IPv6 support:", "✅ Yes" if ipv6_supported else "❌ No")
    print("🔌 IPv6 binding test:", "✅ Yes" if test_bind_ipv6() else "❌ No")
    print("🔌 IPv4 binding test:", "✅ Yes" if test_bind_ipv4() else "❌ No")
    
    print("\n🚀 Starting Flask test server...")
    try:
        server_thread = start_flask_test_server()
        print("✅ Flask test server started")
        
        print("\n🌐 Testing HTTP connectivity...")
        results = test_http_connectivity()
        
        print("🌐 IPv4 connectivity:", "✅ Success" if results['ipv4'] else f"❌ Failed - {results.get('ipv4_error', 'Unknown error')}")
        
        if ipv6_supported:
            print("🌐 IPv6 connectivity:", "✅ Success" if results['ipv6'] else f"❌ Failed - {results.get('ipv6_error', 'Unknown error')}")
        else:
            print("🌐 IPv6 connectivity: ⚠️  Skipped (system doesn't support IPv6)")
        
        if results['ipv4'] and (not ipv6_supported or results['ipv6']):
            print("\n🎉 All tests passed! The application supports IPv4 and IPv6 where available.")
        elif results['ipv4']:
            print("\n✅ IPv4 works correctly. IPv6 support depends on system configuration.")
        else:
            print("\n❌ IPv4 connectivity failed.")
            
    except Exception as e:
        print(f"❌ Error starting test server: {e}")

if __name__ == "__main__":
    main()