import torch
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from transformers import BertTokenizer, BertForSequenceClassification
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from pymongo import MongoClient
from datetime import datetime

# 🔹 Initialize Flask App & SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# 🔹 MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["Scraped_data"]
collection = db["Webcrawl_data"]

# 🔹 Load BERT Model
bert_tokenizer = BertTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
bert_model = BertForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")

# 🔹 Load LSTM Model
lstm_model = load_model("lstm_model.h5")  # Ensure LSTM model is trained & saved

# 🔹 Sentiment Analysis Function
def analyze_sentiment(text):
    inputs = bert_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = bert_model(**inputs)
    sentiment_score = torch.argmax(outputs.logits).item()

    # Convert to Human-Readable Sentiment
    sentiment_map = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}
    return sentiment_map[sentiment_score]

# 🔹 Fetch Data & Perform Sentiment Analysis
@app.route("/analyze", methods=["GET"])
def analyze_data():
    all_data = list(collection.find({}, {"_id": 0, "content": 1}))

    sentiment_counts = {"Very Negative": 0, "Negative": 0, "Neutral": 0, "Positive": 0, "Very Positive": 0}
    analyzed_results = []

    for data in all_data:
        text = data.get("content", "")
        if text:
            sentiment = analyze_sentiment(text)
            sentiment_counts[sentiment] += 1
            analyzed_results.append({"text": text[:200], "sentiment": sentiment})  # Show first 200 chars

    # Send Real-Time Data to Frontend
    socketio.emit("update_graph", sentiment_counts)

    return jsonify({"sentiments": sentiment_counts, "results": analyzed_results})

# 🔹 Render Dashboard
@app.route("/")
def index():
    return render_template("index.html")

# 🔹 Run Flask App
if __name__ == "__main__":
    socketio.run(app, debug=True)
