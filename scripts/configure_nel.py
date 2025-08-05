import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
CLOUDFLARE_API_KEY = os.getenv('CLOUDFLARE_API_KEY')
CLOUDFLARE_EMAIL = os.getenv('CLOUDFLARE_EMAIL')
ZONE_ID = '5d457b0db02ae32d7af7cef5c6d745b5'

# API endpoint
url = f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/settings/nel'

# Headers
headers = {
    'X-Auth-Email': CLOUDFLARE_EMAIL,
    'X-Auth-Key': CLOUDFLARE_API_KEY,
    'Content-Type': 'application/json'
}

# NEL configuration - customize these values
nel_config = {
    "enabled": True,
    "max_age": 604800,
    "include_subdomains": False,
    "report_to": "default",
    "sample_rate": 0.1
}

# Create payload
payload = {
    "value": nel_config
}

try:
    # Make PATCH request
    response = requests.patch(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    
    # Handle response
    result = response.json()
    if result['success']:
        print("NEL configuration updated successfully!")
        print(json.dumps(result['result'], indent=2))
    else:
        print("Error updating NEL configuration:")
        print(json.dumps(result['errors'], indent=2))
        
except requests.exceptions.RequestException as e:
    print(f"API request failed: {str(e)}")
    if hasattr(e, 'response') and e.response.text:
        print("Server response:", e.response.text)