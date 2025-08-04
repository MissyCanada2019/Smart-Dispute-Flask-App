import os
import requests
from .error_handling import handle_exception

def get_ssl_certificate_packs():
    """Retrieve SSL certificate packs from Cloudflare"""
    try:
        api_key = os.getenv('CLOUDFLARE_API_KEY')
        if not api_key:
            raise ValueError("Cloudflare API key not found in environment variables")
            
        zone_id = "5d457b0db02ae32d7af7cef5c6d745b5"
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/ssl/certificate_packs"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        handle_exception(e, "Cloudflare API Error")
        return None