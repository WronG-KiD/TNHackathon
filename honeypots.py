import time
import logging
import requests
import scrapy
import asyncio
import aiohttp
import random
from flask import Flask, request, jsonify
from pymongo import MongoClient
from telethon.sync import TelegramClient
from scrapy.crawler import CrawlerProcess
from scapy.all import sniff

# 🚀 MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["honeypot_data"]
collections = {
    "web": db["web_honeypot"],
    "telegram": db["telegram_honeypot"],
    "darkweb": db["darkweb_honeypot"],
    "network": db["network_honeypot"]
}

# 🔥 1️⃣ WEB HONEYPOT (Detect Bot Scanners)
app = Flask(__name__)

@app.route("/")
def fake_home():
    ip = request.remote_addr
    collections["web"].insert_one({"ip": ip, "endpoint": "/", "time": time.time()})
    return "Welcome to our secure server! 🚀"

@app.route("/admin")
def fake_admin():
    ip = request.remote_addr
    collections["web"].insert_one({"ip": ip, "endpoint": "/admin", "alert": "Suspicious Admin Panel Access!", "time": time.time()})
    return "403 Forbidden", 403

@app.route("/hidden")
def fake_hidden():
    ip = request.remote_addr
    collections["web"].insert_one({"ip": ip, "endpoint": "/hidden", "alert": "Bot Crawling Detected!", "time": time.time()})
    return "Nothing to see here!", 404

# 🔥 2️⃣ TELEGRAM HONEYPOT (Track Suspicious Users)
api_id = "YOUR_TELEGRAM_API_ID"
api_hash = "YOUR_TELEGRAM_API_HASH"
honeypot_group = "your_honeypot_group"

async def monitor_telegram():
    async with TelegramClient("honeypot_bot", api_id, api_hash) as client:
        async for message in client.iter_messages(honeypot_group):
            if any(keyword in message.text.lower() for keyword in ["hack", "carding", "malware"]):
                collections["telegram"].insert_one({
                    "user": message.sender_id,
                    "message": message.text,
                    "time": message.date
                })
                print(f"🚨 ALERT: Suspicious Telegram Activity - {message.text}")

# 🔥 3️⃣ DARK WEB HONEYPOT (Fake Marketplace)
class DarkWebHoneypotSpider(scrapy.Spider):
    name = "darkweb_honeypot"
    allowed_domains = ["example.onion"]
    start_urls = ["http://example.onion/marketplace"]

    def parse(self, response):
        for user in response.css("div.user"):
            data = {
                "username": user.css("h2::text").get(),
                "item": user.css("p.item::text").get(),
                "price": user.css("span.price::text").get(),
                "ip": response.headers.get("X-Forwarded-For", "Unknown"),
                "time": time.time()
            }
            if not collections["darkweb"].find_one({"username": data["username"]}): 
                collections["darkweb"].insert_one(data)

def run_darkweb_honeypot():
    process = CrawlerProcess()
    process.crawl(DarkWebHoneypotSpider)
    process.start()

# 🔥 4️⃣ NETWORK HONEYPOT (Monitor for Bot Scanners)
def detect_network_attack(packet):
    if packet.haslayer("IP"):
        src_ip = packet["IP"].src
        if src_ip not in ["192.168.1.1"]:  # Ignore local IPs
            collections["network"].insert_one({"ip": src_ip, "alert": "Potential Port Scanning!", "time": time.time()})
            print(f"⚠ ALERT: Potential port scanning detected from {src_ip}")

# 🚀 RUN ALL HONEYPOTS ASYNCHRONOUSLY
async def run_honeypots():
    print("🔥 Deploying Honeypots...")

    # Start the web honeypot (Flask)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, app.run, "0.0.0.0", 8080)

    # Start the dark web honeypot (Scrapy)
    loop.run_in_executor(None, run_darkweb_honeypot)

    # Start the network honeypot (Packet sniffing)
    loop.run_in_executor(None, sniff, {"prn": detect_network_attack, "store": 0})

    # Start Telegram Honeypot Monitoring
    await monitor_telegram()

# Run all honeypots
asyncio.run(run_honeypots())