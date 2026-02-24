from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import pandas as pd
from textblob import TextBlob

app = Flask(__name__)
CORS(app)

# ----------------------------
# MongoDB Connection
# ----------------------------
import os

client = MongoClient(os.environ.get("MONGO_URI"))

db = client["covid_db"]
collection = db["tweets"]


# ----------------------------
# Sentiment Function
# ----------------------------
def get_sentiment(text):
    analysis = TextBlob(str(text))
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        return "Positive", polarity
    elif polarity < 0:
        return "Negative", polarity
    else:
        return "Neutral", polarity


# ----------------------------
# Analyze Dataset Route
# ----------------------------
@app.route("/analyze")
def analyze():
    try:
        df = pd.read_csv("small_dataset.csv")

        # Drop rows where clean_tweet is missing
        df = df.dropna(subset=["clean_tweet"])

        # ⚠ Clear old data (prevents duplicate insert)
        collection.delete_many({})

        data_to_insert = []

        for index, row in df.iterrows():
            tweet_text = str(row["clean_tweet"])

            sentiment, polarity = get_sentiment(tweet_text)

            data_to_insert.append({
                "tweet": tweet_text,
                "sentiment": sentiment,
                "polarity": polarity
            })

        # Bulk insert (faster than insert_one)
        collection.insert_many(data_to_insert)

        return jsonify({
            "message": "Dataset analyzed and stored successfully",
            "records_inserted": len(data_to_insert)
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# ----------------------------
# Stats Route
# ----------------------------
@app.route("/stats")
def stats():
    total = collection.count_documents({})
    positive = collection.count_documents({"sentiment": "Positive"})
    negative = collection.count_documents({"sentiment": "Negative"})
    neutral = collection.count_documents({"sentiment": "Neutral"})

    return jsonify({
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral
    })


# ----------------------------
# Run Server
# ----------------------------
# if __name__ == "__main__":
#     app.run(debug=True)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)