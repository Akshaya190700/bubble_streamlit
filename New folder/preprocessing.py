import re
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize
from textblob import TextBlob
import nltk

# Ensure nltk resources are downloaded
nltk.download('punkt')
nltk.download('wordnet')

# Initialize lemmatizer and stemmer
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["bubble_db"]
users_collection = db['bubble_users']
posts_collection = db['bubble_posts']

def preprocess_text(text, use_stemming=False, use_lemmatization=True):
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove special characters
    text = re.sub(r'[(),@#$%^&*!]', '', text)

    # Replace URLs with [URL]
    text = re.sub(r'https?://\S+|www\.\S+', '[URL]', text)

    # Replace email addresses with [EMAIL]
    text = re.sub(r'\b[\w.%+-]+@[\w.-]+\.\w{2,}\b', '[EMAIL]', text)

    # Remove emojis
    text = re.sub(r'[\U00010000-\U0010ffff]|[\u2600-\u26FF]', '', text, flags=re.UNICODE)

    # Handle numerical values (remove commas)
    text = re.sub(r'(?<=\d),(?=\d)', '', text)
    
    # Tokenize text
    tokens = word_tokenize(text)

    # Apply stemming or lemmatization
    if use_stemming:
        tokens = [stemmer.stem(token) for token in tokens]
    if use_lemmatization:
        tokens = [lemmatizer.lemmatize(token) for token in tokens]

    # Rejoin tokens into a single string
    text = ' '.join(tokens)

    return text

def analyze_sentiment(text):
    """
    Analyze the sentiment of the text using TextBlob.
    Returns 'Positive', 'Negative', or 'Neutral'.
    """
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Fetch documents from the collection
for document in posts_collection.find({"process flag": False}):
    content = document.get('content', '')

    if content:
        # Process the content field
        processed_text = preprocess_text(content)

        # Analyze sentiment
        sentiment = analyze_sentiment(processed_text)

        # Update the document with processed_text and sentiment fields
        posts_collection.update_one(
            {"_id": document["_id"]},
            {"$set": {
                "processed_text": processed_text,
                "sentiment": sentiment,
                "process flag": True
                }}
        )
print("Processing complete. All content fields have been updated with processed_text and sentiment")
