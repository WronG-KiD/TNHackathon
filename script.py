import asyncio
import aiohttp
import requests
import hashlib
import time
import scrapy
import tweepy
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from telethon.sync import TelegramClient

# 🔹 MongoDB Configuration (Single Collection)
client = MongoClient("mongodb://localhost:27017/")
db = client["Scraped_data_db"]
collection = db["Scraped_data"]  # Single collection for all data

# 🔹 TOR Proxy Configuration
proxies = {
    "http": "socks5h://127.0.0.1:9150",
    "https": "socks5h://127.0.0.1:9150",
}

# 🔹 Dark Web Search Engines & Predefined URLs
search_engines = [
    "https://ahmia.fi/search/?q=darknet",
    "https://ahmia.fi/search/?q=market",
    "http://3g2upl4pq6kufc4m.onion/",
    "http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion/wiki/index.php/Main_Page"
    "http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion",  
    "http://darksearch.io",
    "http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion",
    "http://hss3uro2hsxfogfq.onion", 
    "http://l4rsciqnpzdndt2llgjx3luvnxip7vbyj6k6nmdy4xs77tx6gkd24ead.onion",
    "http://phobosxilamwcg75xt22id7aywkzol6q6rfl2flipcqoc4e4ahima5id.onion",
    "http://3fzh7yuupdfyjhwt3ugzqqof6ulbcl27ecev33knxe3u7goi3vfn2qqd.onion", 
    "http://no6m4wzdexe3auiupv2zwif7rm6qwxcyhslkcnzisxgeiw6pvjsgafad.onion",  
    "http://torgle5fj664v7pf.onion",  
    "http://onionf4j3fwqpeo5.onion", 
    "http://tordex7iie7z2wcg.onion",  
    "http://tor66sewebgixwhcqfnp5inzp5x5uohhdy3kvtnyfxc2e5mxiuh34iid.onion",
    "http://tormaxunodsbvtgo.onion",
    "http://haystak5njsmn2hqkewecpaxetahtwhsbsa64jom2k22z5afxhnpxfid.onion",
    "http://multivacigqzqqon.onion",  
    "http://evo7no6twwwrm63c.onion",  
    "http://deeplinkdeatbml7.onion",
]

predefined_urls = [
    "https://www.torproject.org/", 
    "https://www.reddit.com/r/darknet/", 
    "https://www.privacytools.io/", 
    "https://www.eff.org/", 
    "https://www.securityweek.com/", 
    "https://www.wired.com/category/tech/", 
    "http://zqktlwiuavvvqqt4ybvg6qle25ymkcy6kwvfngonb36cfcobygayydid.onion",
    "http://3g2upl4pq6kufc4m.onion",
    "http://msydqstlz2kzerdg.onion",
    "http://gfg57xhwyj4mmb4r.onion",
    "http://xmh57jrzrnw6insl.onion",
    "https://www.darknetmarkets.co/",
    "https://www.reddit.com/r/darkwebmarkets/",
    "https://www.reddit.com/r/onions/",
    "https://www.exploit-db.com/",
    "https://www.zeroday.today/",
    "https://www.hackaday.com/",
    "https://www.cybrary.it/",
    "https://www.virustotal.com/",
    "https://www.malwarebytes.com/",
    "https://www.virscan.org/",
    "https://www.cybereason.com/",
    "http://dwltorbltw3tdjskxn23j2mwz2f4q25j4ninl5bdvttiy4xb6cqzikid.onion/",
    "http://s4k4ceiapwwgcm3mkb6e4diqecpo7kvdnfr5gg7sph7jjppqkvwwqtyd.onion",
    "http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion/wiki/index.php/Main_Page",
    "http://paavlaytlfsqyvkg3yqj7hflfg5jw2jdg2fgkza5ruf6lplwseeqtvyd.onion/",
    "http://2jwcnprqbugvyi6ok2h2h7u26qc6j5wxm7feh3znlh2qu3h6hjld4kyd.onion/",
    "http://underdiriled6lvdfgiw4e5urfofuslnz7ewictzf76h4qb73fxbsxad.onion",
    "http://torlisthsxo7h65pd2po7kevpzkk4wwf3czylz3izcmsx4jzwabbopyd.onion/",
    "http://jgwe5cjqdbyvudjqskaajbfibfewew4pndx52dye7ug3mt3jimmktkid.onion/",
    "http://torlinksge6enmcyyuxjpjkoouw4oorgdgeo7ftnq3zodj7g2zxi3kyd.onion/",
    "http://deeeepv4bfndyatwkdzeciebqcwwlvgqa6mofdtsvwpon4elfut7lfqd.onion/"
]

# 🔹 Function to Extract `.onion` URLs
def extract_onion_links():
    extracted_urls = set()
    session = requests.Session()
    session.proxies = proxies

    for search_url in search_engines:
        try:
            response = session.get(search_url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for link in soup.find_all("a"):
                    url = link.get("href")
                    if url and ".onion" in url and not collection.find_one({"url": url}):
                        extracted_urls.add(url)
                        collection.insert_one({"url": url, "source": "search_engine"})
            else:
                print(f"⚠️ Failed to fetch {search_url} (HTTP {response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"🚫 Error fetching {search_url}: {e}")

    return extracted_urls

all_urls = predefined_urls + list(extract_onion_links())

# 🔹 Scrape Dark Web Content
session = requests.Session()
session.proxies = proxies

for url in all_urls:
    try:
        if collection.find_one({"url": url}):
            print(f"🔄 Skipping already scraped URL: {url}")
            continue

        response = session.get(url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text_data = soup.get_text()
            content_hash = hashlib.sha256(text_data.encode('utf-8')).hexdigest()

            if collection.find_one({"content_hash": content_hash}):
                print(f"🛑 Duplicate Content Found! Skipping {url}")
                continue

            collection.insert_one({
                "url": url,
                "content": text_data,
                "content_hash": content_hash,
                "source": "dark_web",
                "timestamp": datetime.utcnow()
            })
            print(f"✅ Data stored for: {url}")
            time.sleep(2)

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error scraping {url}: {e}")

# 🔹 ThreatExchange API
THREATEXCHANGE_ACCESS_TOKEN = "EAAJGVnkIZBfUBOxZCBGcUNkfhPkvtPZA73VPDGW3ptEZBfejjozYVwOPqJdtL1ZBU1cUDI3lVTn0igutkj9CjAPOsboegZC6Uew2ghoR26R9F7EkZBQpAsSTmrQcZARtSSMYknHYBCS2tBjOJdvasatLiyXQuojg5IBX8UsPaG0a6Y956HO0TucTGuGa"
THREATEXCHANGE_URL = "https://graph.facebook.com/v18.0/threat_indicators"

async def fetch_threat_exchange():
    params = {
        "access_token": THREATEXCHANGE_ACCESS_TOKEN,
        "limit": 100,
        "fields": "indicator,type,confidence,severity,review_status,share_level"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(THREATEXCHANGE_URL, params=params) as response:
            data = await response.json()
            for threat in data.get("data", []):
                if not collection.find_one({"indicator": threat["indicator"]}):
                    collection.insert_one({"source": "ThreatExchange", **threat})

# 🔹 Dark Web Scraper using Scrapy
class DarkWebSpider(scrapy.Spider):
    name = "darkweb"
    start_urls = all_urls

    def parse(self, response):
        for post in response.css("div.post"):
            data = {
                "title": post.css("h2::text").get(),
                "content": post.css("p::text").get(),
                "link": response.urljoin(post.css("a::attr(href)").get()),
                "timestamp": datetime.utcnow(),
                "source": "dark_web"
            }
            if not collection.find_one({"link": data["link"]}):
                collection.insert_one(data)
                yield data

def run_darkweb_scraper():
    process = CrawlerProcess()
    process.crawl(DarkWebSpider)
    process.start()

# 🔹 Telegram Scraper
api_id = "12846325"
api_hash = "bd5d779ee1d29b84409efdb1d3bf65c8"
groups = ["group1", "group2"]

async def fetch_telegram():
    async with TelegramClient("anon", api_id, api_hash) as client:
        for group in groups:
            async for message in client.iter_messages(group, limit=100):
                post = {"group": group, "message": message.text, "date": message.date, "source": "Telegram"}
                if not collection.find_one({"message": post["message"]}):
                    collection.insert_one(post)

# 🔹 Twitter Scraper
twitter_bearer_token = "AAAAAAAAAAAAAAAAAAAAAF6pygEAAAAAEdhFuXxwCcliXch%2B5myuDQcrFZA%3D8IXI8AbwfAECiadUqcu78AIQtZX8qfZKddjH36pPK3s1SRORyG"
twitter_client = tweepy.Client(bearer_token=twitter_bearer_token)

async def fetch_twitter():
    query = "#darkweb OR #hacking"
    tweets = twitter_client.search_recent_tweets(query=query, tweet_fields=["created_at"], max_results=100)
    for tweet in tweets.data:
        tweet_data = {"tweet": tweet.text, "date": tweet.created_at, "source": "Twitter"}
        if not collection.find_one({"tweet": tweet_data["tweet"]}):
            collection.insert_one(tweet_data)

# 🔹 Instagram Scraper
ACCESS_TOKEN = "EAAy2t6sQcicBO8tRcPaqOlaPTNvsAe2J23HEHICxxaZCnwhvRp2ZCyERaKN4cI0elpisKzrho66sh35TX9rHobBvVcYklmLezhoi3Dy9Mtu7er1feJ036PjYi2INTBikSyjkmM4jVz8aO2xbsxJLWqrZCRla0mstlq0y9E1jVlKwIubCa6ZAeuZCM"
INSTAGRAM_ID = "weakkk_"

async def fetch_instagram():
    url = f"https://graph.instagram.com/{INSTAGRAM_ID}/media?fields=id,caption,media_url&access_token={ACCESS_TOKEN}"
    posts = requests.get(url).json()
    for post in posts["data"]:
        post_data = {"id": post["id"], "caption": post["caption"], "source": "Instagram"}
        if not collection.find_one({"id": post_data["id"]}):
            collection.insert_one(post_data)

# 🔹 Facebook Scraper
FACEBOOK_PAGE_ID = "555414830991024"


async def fetch_facebook():
    url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/posts?fields=message,created_time&access_token={ACCESS_TOKEN}"
    posts = requests.get(url).json()
    for post in posts["data"]:
        post_data = {"id": post["id"], "message": post["message"], "source": "Facebook"}
        if not collection.find_one({"id": post_data["id"]}):
            collection.insert_one(post_data)

# 🔹 Scheduler
scheduler = AsyncIOScheduler()

async def run_scrapers():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_darkweb_scraper)
    await asyncio.gather(fetch_telegram(), fetch_twitter(), fetch_instagram(), fetch_facebook(), fetch_threat_exchange())

scheduler.add_job(run_scrapers, "interval", minutes=30)
scheduler.start()

async def main():
    await run_scrapers()

asyncio.run(main())
