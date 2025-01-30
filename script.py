import requests
from bs4 import BeautifulSoup
from store_data import save_to_mongo

proxies = {
    "http": "socks5h://127.0.0.1:9150",
    "https": "socks5h://127.0.0.1:9150",
}

url = "https://www.torproject.org/" 
response = requests.get(url, proxies=proxies)

soup = BeautifulSoup(response.text, "html.parser")
text_data = soup.get_text()

data = {"url": url, "content": text_data}
save_to_mongo(data)  # Save to MongoDB
