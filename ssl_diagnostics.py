import socket
import ssl
import http.client

def check_ssl_certificate(domain):
    """Check SSL certificate details using standard libraries"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
        print(f"✅ SSL certificate for {domain}:")
        print(f"  Issuer: {cert['issuer']}")
        print(f"  Valid From: {cert['notBefore']}")
        print(f"  Valid Until: {cert['notAfter']}")
        print(f"  SANs: {cert.get('subjectAltName', [])}")
        return True
    except Exception as e:
        print(f"❌ SSL certificate check failed for {domain}: {str(e)}")
        return False

def check_https_connectivity(domain):
    """Check HTTPS connectivity using http.client"""
    try:
        conn = http.client.HTTPSConnection(domain, timeout=5)
        conn.request("HEAD", "/")
        response = conn.getresponse()
        print(f"✅ HTTPS connectivity to {domain}:")
        print(f"  Status Code: {response.status}")
        print(f"  Server: {response.getheader('Server', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ HTTPS connection failed for {domain}: {str(e)}")
        return False

def main():
    domain = "justice-bot.com"
    subdomain = "app.justice-bot.com"
    
    print(f"🔒 SSL Diagnostics for {domain}")
    print("="*50)
    
    # Check main domain certificate
    check_ssl_certificate(domain)
    
    # Check subdomain certificate
    check_ssl_certificate(subdomain)
    
    # Test HTTPS connectivity
    check_https_connectivity(domain)
    check_https_connectivity(subdomain)
    
    print("="*50)
    print("Diagnostics complete. Review output for any errors.")

if __name__ == "__main__":
    main()