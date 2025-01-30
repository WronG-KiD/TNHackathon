from pymongo import MongoClient

def save_to_mongo(data):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["tor_scraper"]
    collection = db["scraped_data"]
    collection.insert_one(data)
    print("✅ Data saved to MongoDB!")
