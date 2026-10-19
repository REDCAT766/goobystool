import sys
import json
import urllib.request
import urllib.error
import threading
from datetime import datetime

LOG_FILE = "goobytools_scan_logs.json"

# Example structural destination list (You can add any public URL or IP block here)
TARGET_POOL = [
    "http://127.0.0",  # Your local backend server
    "https://httpbin.org",            # Public HTTP test container mirror
    "http://1.1.1",                      # Public CDN DNS Anycast Core
    "http://8.8.8"                       # Alternative verification node
]

def send_payload_sync(url, json_bytes, results, index):
    """Sends information using standard native library handlers."""
    try:
        req = urllib.request.Request(
            url, 
            data=json_bytes, 
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        # 3-second timeout ensures slow external routes do not lock up the tool thread
        with urllib.request.urlopen(req, timeout=3) as response:
            results[index] = (url, f"HTTP {response.status}")
    except urllib.error.HTTPError as e:
        results[index] = (url, f"HTTP {e.code}")
    except urllib.error.URLError:
        results[index] = (url, "CONN_FAIL")
    except Exception:
        results[index] = (url, "TIMEOUT/ERR")

def run_mass_scan(payload):
    """Dispatches parallel multi-threading tasks across every target server address."""
    print(f"[System] Initiating parallel connections to {len(TARGET_POOL)} destinations using goobytools network matrix...")
    
    # Convert data payload into standardized JSON bytes once
    json_bytes = json.dumps(payload).encode('utf-8')
    
    threads = []
    results = [None] * len(TARGET_POOL)
    
    # Spin up separate concurrent workers for every single target item
    for i, url in enumerate(TARGET_POOL):
        t = threading.Thread(target=send_payload_sync, args=(url, json_bytes, results, i))
        threads.append(t)
        t.start()
        
    # Wait until every single thread finishes its network request
    for t in threads:
        t.join()
        
    return results

def run_tool():
    print("=========================================")
    print("      GOOBYTOOLS - Global Mass Tester    ")
    print("=========================================")
    
    # 1. Verification Opt-In Guard
    enable_input = input("Enable data collection and broad network scan? (y/n): ").strip().lower()
    if enable_input != 'y':
        print("\n[System] Operation aborted by user choice.")
        sys.exit(0)
        
    username = input("\nEnter test username: ").strip()
    email = input("Enter test email address: ").strip()
    
    if not username or not email:
        print("[Error] Input fields cannot be left empty.")
        return

    payload = {"username": username, "email": email}
    
    print("\n--- Starting Broadcast Scan ---")
    start_time = datetime.now()
    
    # 2. Trigger Concurrent Threading Pool Engine
    scan_results = run_mass_scan(payload)
    
    # 3. Print Performance Analytics Dashboard
    print("\n=========================================")
    print("             SCAN RESULTS                ")
    print("=========================================")
    print(f"{'Target URL':<40} | {'Status':<12}")
    print("-" * 55)
    
    log_data = []
    for item in scan_results:
        if item is None:
            continue
        url, status = item
        display_url = url if len(url) <= 40 else url[:37] + "..."
        print(f"{display_url:<40} | {status:<12}")
        
        log_data.append({
            "url": url,
            "status": status,
            "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    # Save results directly to disk log structure
    with open(LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=4)
        
    print(f"\n[System] Scan complete in {(datetime.now() - start_time).total_seconds():.2f} seconds.")
    print(f"Results recorded in '{LOG_FILE}'.")

if __name__ == "__main__":
    run_tool()
