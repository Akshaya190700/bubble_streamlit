import random
from pymongo import MongoClient
from bson import ObjectId

# CONNECTION_STRING = "mongodb+srv://freego:freego%2322Monkey@freego-c0.y47x2e3.mongodb.net/user_recommendation?retryWrites=true&w=majority"

CONNECTION_STRING="mongodb://localhost:27017/"
client = MongoClient(CONNECTION_STRING)
db = client['bubble_database']
users_collection = db['bubble_users']
posts_collection = db['bubble_posts']

# Load sentences from text file
with open("rough data 01.txt", "r") as file:
    sentences = file.readlines()
# print(sentences)

# Shuffle sentences
random.shuffle(sentences)

# # Fetch user IDs from MongoDB
user_ids = [str(user["_id"]) for user in users_collection.find({}, {"_id": 1})]
# print(user_ids)

# Check if sentence count is enough
if len(sentences) < len(user_ids) * 4:
    print("Not enough sentences to distribute.")
else:
    # Assign sentences to users
    for i, user_id in enumerate(user_ids):
        assigned_sentences = sentences[i*4:(i+1)*4]
        users_collection.update_one(
            {"_id": user_id},
            {"$set": {"assigned_sentences": assigned_sentences}}
        )
    print("Sentences assigned successfully.")
