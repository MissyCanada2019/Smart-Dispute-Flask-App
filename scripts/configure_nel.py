import os
import requests
import json
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# Load environment variables
load_dotenv()
CLOUDFLARE_API_KEY = os.getenv('CLOUDFLARE_API_KEY')
CLOUDFLARE_EMAIL = os.getenv('CLOUDFLARE_EMAIL')
ZONE_ID = '5d457b0db02ae32d7af7cef5c6d745b5'

# Create robust session with retry logic
def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["PATCH"],
        respect_retry_after_header=True
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    return session

# API endpoint
url = f'https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/settings/nel'

# Headers
headers = {
    'X-Auth-Email': CLOUDFLARE_EMAIL,
    'X-Auth-Key': CLOUDFLARE_API_KEY,
    'Content-Type': 'application/json'
}

# NEL configuration
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
    session = create_session()
    response = session.patch(url, headers=headers, data=json.dumps(payload), timeout=(3, 10))
    response.raise_for_status()
    
    result = response.json()
    if result['success']:
        print("NEL configuration updated successfully!")
        print(json.dumps(result['result'], indent=2))
    else:
        print("Error updating NEL configuration:")
        print(json.dumps(result['errors'], indent=2))
        
except Exception as e:
    print(f"Critical error: {str(e)}")
    if hasattr(e, 'response') and e.response.text:
        print("Server response:", e.response.text)