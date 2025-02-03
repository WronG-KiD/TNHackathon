from flask import Flask, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from collections import defaultdict

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db_tor_scraper = client["tor_scraper"]
db_crawled_data = client["crawled_data_db"]
db_honeypot = client["honeypot_data_db"]

# Collections
collections = {
    "scraped_data": db_tor_scraper["scraped_data"],
    "failed_data": db_tor_scraper["failed_data"],
    "crawled_data": db_crawled_data["crawled_data"],
    "attacks": db_honeypot["attacks"]
}

# Function to merge data by URL
def fetch_and_merge_data():
    url_data = defaultdict(lambda: {
        "id": None,
        "access": "Yes",
        "safe_or_not": "Depends",
        "malicious_activity": set(),
        "content": set(),
        "mitigation_solution": set()
    })

    for collection_name, collection in collections.items():
        cursor = collection.find({}, {"_id": 1, "url": 1, "category": 1, "description": 1, "content": 1, "attack_type": 1, "mitigation_steps": 1})
        for item in cursor:
            url = item.get("url", "Unknown URL")
            
            if collection_name == "failed_data":
                # Failed Data: Different URL and default values
                url_data[url] = {
                    "id": str(item["_id"]),
                    "access": "No",
                    "safe_or_not": "N/A",
                    "malicious_activity": "N/A",
                    "content": "N/A",
                    "mitigation_solution": "N/A"
                }
            else:
                # Other Collections: Merge data
                url_data[url]["id"] = str(item["_id"])
                url_data[url]["access"] = "Yes"
                url_data[url]["safe_or_not"] = "Not Safe" if collection_name in ["scraped_data", "attacks"] else "Depends"

                if "description" in item:
                    url_data[url]["malicious_activity"].add(item["description"])
                if "attack_type" in item:
                    url_data[url]["malicious_activity"].add(item["attack_type"])
                if "content" in item:
                    url_data[url]["content"].add(item["content"])
                if "mitigation_steps" in item:
                    url_data[url]["mitigation_solution"].add(item["mitigation_steps"])

    # Convert sets to strings
    merged_data = []
    for index, (url, details) in enumerate(url_data.items(), start=1):
        merged_data.append({
            "sno": index,
            "id": details["id"],
            "url": url,
            "access": details["access"],
            "safe_or_not": details["safe_or_not"],
            "malicious_activity": "; ".join(details["malicious_activity"]) if isinstance(details["malicious_activity"], set) else details["malicious_activity"],
            "content": "; ".join(details["content"])[:200] + "..." if isinstance(details["content"], set) else details["content"],
            "mitigation_solution": "; ".join(details["mitigation_solution"]) if isinstance(details["mitigation_solution"], set) else details["mitigation_solution"]
        })

    return merged_data

@app.route('/api/merged_data', methods=['GET'])
def get_merged_data():
    data = fetch_and_merge_data()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
