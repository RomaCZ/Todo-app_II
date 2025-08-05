import requests
import json

def test_server():
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Test main dashboard
        response = requests.get(f"{base_url}/")
        print(f"Dashboard Status: {response.status_code}")
        
        # Test contracts API
        response = requests.get(f"{base_url}/api/v1/contracts/debug/all")
        print(f"Contracts API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total contracts: {data.get('total_count', 0)}")
        
        # Test manual processing interface
        response = requests.get(f"{base_url}/api/v1/manual-processing")
        print(f"Manual Processing Status: {response.status_code}")
        print(f"Content Type: {response.headers.get('content-type', 'unknown')}")
        
        # Test contract data API
        response = requests.get(f"{base_url}/api/v1/manual-processing/contract-data")
        print(f"Contract Data API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Contracts for manual processing: {data.get('total_count', 0)}")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_server()
