import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"
TOPICS = [
    "Impact of climate change on ocean biodiversity",
    "Advancements in solid-state battery technology",
    "The role of AI in personalized education",
    "Structural biology of viral spike proteins",
    "Sustainable urban planning in smart cities"
]

def check_topic(topic):
    print(f"\n>>> Checking Topic: {topic}")
    start_time = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/api/submit",
            json={"query": topic},
            timeout=300
        )
        duration = time.time() - start_time
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success (Took {duration:.1f}s)")
            print(f"   Plan Goal: {data.get('plan', {}).get('goal')}")
            print(f"   Execution: {data.get('execution', {}).get('successful')}/{data.get('execution', {}).get('total_results')} tasks successful")
            print(f"   Trusted Items: {data.get('execution', {}).get('trusted_items')}")
            
            insights = data.get('insights', {})
            if isinstance(insights, dict):
                summary = insights.get('summary', 'No summary')
            else:
                summary = str(insights)[:100] + "..."
            print(f"   Insight Summary: {summary[:150]}...")
        else:
            print(f"❌ Failed (Status: {response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❗ Error: {e}")

if __name__ == "__main__":
    print("Starting 5-topic agent verification...")
    # Verify status first
    try:
        status = requests.get(f"{BASE_URL}/api/status").json()
        print(f"System Status: {'Connected' if status.get('success') else 'Failed'}")
    except:
        print("System offline? Check if server is running on port 5000.")
        exit(1)

    for topic in TOPICS:
        check_topic(topic)
    
    print("\nVerification complete.")
