import requests
from pymongo import MongoClient
import time

# 🔹 MongoDB Configuration
client = MongoClient('localhost', 27017)
db = client['Scraped_data_db']
scraped_collection = db['Scraped_data']  
crawl_collection = db['Webcrawl_data'] 

# 🔹 Threat Categories with Keywords
threat_categories = {
    "Phishing": ["login", "sign in", "account recovery", "verify identity", "bank account"],
    "Hacking": ["exploit", "sql injection", "malware", "trojan", "ransomware", "XSS"],
    "Dark Market": ["buy drugs", "firearms for sale", "counterfeit money", "fake passport"],
    "Scams": ["bitcoin giveaway", "investment scam", "Ponzi scheme", "wire transfer scam"],
    "Illegal Content": ["child abuse", "human trafficking", "gore videos", "live murder stream"],
    "Financial Fraud": ["stolen credit card", "identity theft", "bank fraud", "carding"], 
    "Crypto Fraud": ["bitcoin mixer", "crypto scam", "rug pull scam", "NFT fraud"],
    "Botnets": ["DDoS attack", "botnet for sale", "stresser service", "command and control server"],
    "Dark Web Services": ["bulletproof hosting", "Tor proxy", "VPN service darknet"]
}

# 🔹 Function to Classify URL Safety Based on Content
def classify_url(content):
    """Checks if the webpage contains any malicious keywords and classifies it."""
    detected_categories = []
    
    for category, keywords in threat_categories.items():
        for keyword in keywords:
            if keyword.lower() in content.lower():
                detected_categories.append(category)
                break  # Avoid redundant checks
    
    if detected_categories:
        return "No", detected_categories  # Unsafe
    return "Yes", []  # Safe

# 🔹 Function to Provide Mitigation Steps Based on HTTP Status Codes
def get_mitigation_steps(status_code):
    """Suggests mitigation strategies based on response status code."""
    if status_code == 200:
        return "Monitor traffic, deploy WAF, log attacker IPs."
    elif status_code == 403:
        return "Check firewall rules, block unauthorized access."
    elif status_code == 500:
        return "Inspect server logs, patch vulnerabilities."
    elif status_code == 503:
        return "Check for DDoS attack, scale resources."
    else:
        return "No immediate action required."

# 🔹 Fetch Data from MongoDB and Analyze
def analyze_and_store():
    """Analyzes scraped and extracted URLs, classifies them, and stores in honeypots collection."""
    
    # Combine both scraped and extracted URLs
    urls_data = list(scraped_collection.find())

    for data in urls_data:
        url = data.get("url", "Unknown URL")
        content = data.get("content", "")
        
        # Skip already analyzed URLs
        if crawl_collection.find_one({"url": url}):
            print(f"🔄 URL already analyzed: {url}")
            continue
        
        print(f"🔎 Analyzing: {url}")
        
        # 🔹 Classify if safe or not
        is_safe, detected_threats = classify_url(content)

        # 🔹 Fetch HTTP status if available
        status_code = data.get("status_code", 200)  # Default 200 if not stored

        # 🔹 Get mitigation strategies
        mitigation_steps = get_mitigation_steps(status_code)

        # 🔹 Store in honeypots collection
        crawl_collection.insert_one({
            "url": url,
            "malicious_activity": detected_threats,
            "safe": is_safe,
            "status_code": status_code,
            "mitigation_solutions": mitigation_steps
        })
        
        print(f"✅ Stored {url} in honeypots collection.")

        # Sleep to avoid overwhelming the database
        time.sleep(1)

# 🔹 Run Analysis & Store Results
if __name__ == "__main__":
    analyze_and_store()
