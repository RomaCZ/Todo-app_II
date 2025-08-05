import requests
import json

def test_manual_processing():
    """Test manual processing interface"""
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Test contract data API
        response = requests.get(f"{base_url}/api/v1/manual-processing/contract-data")
        print(f"Contract Data API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total contracts: {data.get('total_count', 0)}")
            
            if data.get('contracts'):
                # Show first contract data
                first_contract = data['contracts'][0]
                print("\nFirst contract data:")
                print(f"  ID: {first_contract.get('id')}")
                print(f"  External ID: {first_contract.get('evidencni_cislo')}")
                print(f"  Title: {first_contract.get('nazev_vz')}")
                print(f"  Contracting Authority: {first_contract.get('zadavatel')}")
                print(f"  Price: {first_contract.get('predp_hodnota_bez_dph')}")
                print(f"  Bid Deadline: {first_contract.get('lhuta_pro_nabidky')}")
                print(f"  Publication Date: {first_contract.get('datum_uverejneni')}")
                print(f"  Form Type: {first_contract.get('typ_formulare')}")
                print(f"  Contract Type: {first_contract.get('druh_zakazky')}")
                print(f"  Procedure: {first_contract.get('rizeni')}")
                print(f"  URL: {first_contract.get('url')}")
                print(f"  Comment: {first_contract.get('komentar')}")
        else:
            print(f"Error: {response.text}")
            
        # Test manual processing page
        response = requests.get(f"{base_url}/api/v1/manual-processing")
        print(f"\nManual Processing Page Status: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes")
        
        if response.status_code == 200 and "zakazka" in response.text:
            print("✓ Manual processing page contains contract-related content")
        else:
            print("⚠ Manual processing page may not be rendering correctly")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_manual_processing()
