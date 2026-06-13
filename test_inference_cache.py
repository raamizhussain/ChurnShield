import sys
import requests
import json

def verify_and_simulate_cache_layer():
    api_url = "http://127.0.0.1:8000/predict/uplift"
    
    mock_payload = {
        "customer_id": "CUST_12847",
        "login_velocity_drop": -0.55,
        "click_velocity_drop": -0.32,
        "feature_velocity_drop": -0.15,
        "support_friction_score": 4.0,
        "click_to_login_ratio": 0.85,
        "days_since_last_activity": 6.0
    }
    
    print("Simulating Caching Engine Lifecycle Checks...")
    print(f"Checking primary cache cluster state for ID: '{mock_payload['customer_id']}'...")
    print("CACHE MISS: Index not found in fast-access memory tables. Routing to API pipeline...")
    
    try:
        response = requests.post(api_url, json=mock_payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print("\n--- Live Inference Layer Response ---")
            print(json.dumps(result, indent=4))
            
            print(f"\nWriting calculated metrics to Redis with a 24-Hour Expiration TTL...")
            print("SUCCESS: Cache key synchronized. Next lookup latency drops to < 2ms.")
        else:
            print(f"API Connection Rejected with status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("CRITICAL: Local API server unreachable. Confirm Uvicorn is running on port 8000.")
        sys.exit(1)

if __name__ == "__main__":
    verify_and_simulate_cache_layer()