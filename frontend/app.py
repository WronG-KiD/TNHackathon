from flask import Flask, render_template
import pymongo

app = Flask(__name__)

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
tor_scraper_db = client["tor_scraper"]
crawled_data_db = client["crawled_data_db"]
honeypot_data_db = client["honeypot_data_db"]

@app.route('/')
def home():
    # Retrieve URL and content from each collection
    tor_scraper_data = tor_scraper_db["scraped_data"].find({}, {"_id": 0, "url": 1})
    crawled_data = crawled_data_db["crawled_data"].find({}, {"_id": 0, "url": 1})
    honeypot_data = honeypot_data_db["attacks"].find({}, {"_id": 0, "url": 1})

    # Create a unified list of all URLs and content
    all_urls = []
    
    # Add data from the tor_scraper collection
    for data in tor_scraper_data:
        all_urls.append({
            "url": data['url'], 
            "source": "tor_scraper"
        })
    
    # Add data from the crawled_data collection
    for data in crawled_data:
        all_urls.append({
            "url": data['url'], 
            "source": "crawled_data"
        })
    
    # Add data from the honeypot_data collection
    for data in honeypot_data:
        all_urls.append({
            "url": data['url'], 
            "source": "honeypot_data"
        })

    return render_template('index.html', all_urls=all_urls)

if __name__ == '__main__':
    app.run(debug=True)
