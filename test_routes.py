import requests
import time

def test_routes():
    base_url = "http://localhost:8080"
    
    # Test routes to check
    routes = [
        "/",
        "/health",
        "/login",
        "/register"
    ]
    
    print("Testing Smart Dispute Canada Application Routes...")
    print("=" * 50)
    
    for route in routes:
        try:
            url = base_url + route
            response = requests.get(url, timeout=5)
            print(f"GET {route}: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"GET {route}: Connection failed (server may not be running)")
        except requests.exceptions.Timeout:
            print(f"GET {route}: Request timed out")
        except Exception as e:
            print(f"GET {route}: Error - {str(e)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_routes()