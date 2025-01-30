import requests
from pymongo import MongoClient
import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Source database (tor_scraper) where honeypot URLs are stored
source_db = client["tor_scraper"]
honeypot_urls_collection = source_db["scraped_data"]  # Collection storing honeypot URLs

# Destination database (honeypot_data_db) to store attack logs
destination_db = client["honeypot_data_db"]
honeypot_logs_collection = destination_db["attacks"]

# Fetch honeypot URLs from `tor_scraper` database
honeypot_urls = [doc["url"] for doc in honeypot_urls_collection.find()]
if not honeypot_urls:
    print("⚠️ No honeypot URLs found in 'tor_scraper' database. Please add some URLs.")
    exit()

print(f"🔍 Found {len(honeypot_urls)} honeypot URLs in 'tor_scraper' database.")

def check_honeypot_urls():
    """Simulate interaction with honeypot URLs and log responses"""
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in honeypot_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            attack_detected = response.status_code != 404  # Consider any non-404 as a potential attack
            log_data = {
                "timestamp": datetime.datetime.utcnow(),
                "url": url,
                "status_code": response.status_code,
                "content_length": len(response.text),
                "attack_detected": attack_detected  # True if attack, False otherwise
            }
            # Insert the log data into MongoDB
            honeypot_logs_collection.insert_one(log_data)
            print(f"✅ Logged honeypot URL: {url} - Status: {response.status_code} - Attack: {attack_detected}")
            print(f"💾 Saved Successfully in MongoDB for {url}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error accessing {url}: {e}")

if __name__ == "__main__":
    print("\n🚀 Checking Honeypot URLs...\n")
    check_honeypot_urls()
    print("\n✅ All honeypot interactions logged in 'honeypot_data_db'!\n")
