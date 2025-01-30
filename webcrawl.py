import requests
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Source database where URLs are stored
source_db = client["tor_scraper"]
urls_collection = source_db["scraped_data"] 

# Destination database for storing crawled data
destination_db = client["crawled_data_db"]
crawled_collection = destination_db["crawled_data"]

# Fetch URLs from the `tor_scraper` database
urls = [doc["url"] for doc in urls_collection.find()]
print(f"🔍 Found {len(urls)} URLs in 'tor_scraper' database.")

def crawl_page(url):
    """Fetch raw text from the given URL"""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.text  # Returns raw page content (including HTML)
        else:
            print(f"❌ Failed to access {url} - Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error accessing {url}: {e}")
        return None

def save_to_mongo(url, text):
    """Store extracted data in the separate database"""
    if text:
        crawled_collection.insert_one({"url": url, "content": text})
        print(f"✅ Data saved for {url}")

# Loop through all URLs, crawl them, and store in a separate DB
for url in urls:
    print(f"🌐 Crawling: {url}")
    raw_text = crawl_page(url)
    if raw_text:
        save_to_mongo(url, raw_text)

print("\n✅ All URLs crawled and data stored in 'crawled_data_db' database!")

# Verify saved data
print("\n📂 Stored Data in MongoDB:")
for doc in crawled_collection.find():
    print(f"🔹 URL: {doc['url']}")
    print(f"📄 Content Length: {len(doc['content'])} characters\n")
