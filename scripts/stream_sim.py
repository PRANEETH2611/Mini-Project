import time
import requests
import random
import json
from datetime import datetime

API_URL = "http://localhost:5000/api/ingest"

def generate_metric():
    """Generate random metric data"""
    # Simulate an incident occasionally
    if random.random() > 0.9:
        cpu = random.uniform(85, 99)
        resp = random.uniform(1000, 3000)
    else:
        cpu = random.uniform(20, 60)
        resp = random.uniform(100, 400)
        
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_usage": round(cpu, 2),
        "memory_usage": round(random.uniform(2, 8), 2),
        "response_time": round(resp, 0)
    }

def stream_data():
    print(f"🚀 Starting Data Stream to {API_URL}...")
    print("Press Ctrl+C to stop.")
    
    while True:
        try:
            data = generate_metric()
            response = requests.post(API_URL, json=data)
            
            if response.status_code == 200:
                print(f"✅ Sent: CPU={data['cpu_usage']}% | Resp={data['response_time']}ms | Total={response.json().get('total_records')}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            print("Make sure backend/app.py is running!")
            
        time.sleep(2) # Send every 2 seconds

if __name__ == "__main__":
    stream_data()
