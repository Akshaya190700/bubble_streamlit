from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# MongoDB Connection
# ConnectionString = "mongodb+srv://freego:freego%2322Monkey@freego-c0.y47x2e3.mongodb.net/user_recommendation?retryWrites=true&w=majority&serverSelectionTimeoutMS=30000&tls=true&tlsAllowInvalidCertificates=true"
# client = MongoClient(ConnectionString)
# # Define database and collection
# db = client["bubble_test"]
# posts_collection = db['bpostone']
client = MongoClient("mongodb://localhost:27017/")
db = client["bubble_db"]
users_collection = db['bubble_users']
posts_collection = db['bubble_posts']

# Load the all_distilroberta-v1 model
model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')


# Process each document in the collection
for post in posts_collection.find({"embedded flag": False, "process flag": True}):
    summarized_text = post.get('summarized_text', '')
    
    if summarized_text:  # Ensure processed_text is not empty or missing
        # Generate the embedding
        embedding = model.encode(summarized_text).tolist()
        
        # Update the document with the embedded_text field
        posts_collection.update_one(
            {'_id': post['_id']},  # Match the document by its _id
            {'$set': {
                'embedded_text': embedding,
                "embedded flag": True
                }}  # Add the embedded_text field and set the flag
        )

print("Embeddings have been successfully added to the MongoDB collection.")
