import re
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB setup
# ConnectionString = "mongodb+srv://freego:freego%2322Monkey@freego-c0.y47x2e3.mongodb.net/user_recommendation?retryWrites=true&w=majority&serverSelectionTimeoutMS=30000&tls=true&tlsAllowInvalidCertificates=true"
# client = MongoClient(ConnectionString)
# # Define database and collection
# db = client["bubble_test"]
client = MongoClient("mongodb://localhost:27017/")
db = client["bubble_db"]
users_collection = db['bubble_users']
posts_collection = db['bubble_posts']

def preprocess_text(text):
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

    return text

# Fetch documents from the collection
for document in posts_collection.find({"process flag": False}):
    content = document.get('content', '')

    if content:
        # Process the content field
        processed_text = preprocess_text(content)

        # Update the document with the processed_text field
        posts_collection.update_one(
            {"_id": document["_id"]},
            {"$set": {
                "processed_text": processed_text,
                "process flag": True
                }}
        )
print("Processing complete. All content fields have been updated with processed_text")
