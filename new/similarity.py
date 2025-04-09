import numpy as np
from pymongo import MongoClient
from datetime import datetime

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["bubble_db"]
users_collection = db['bubble_users']
posts_collection = db['bubble_posts']
similarities_collection = db["similarities"]  # Output collection
metadata_collection = db["batch_metadata"]  # Metadata tracking


def fetch_last_processed_post_number():
    """Retrieve the last processed post number from metadata."""
    metadata = metadata_collection.find_one({"_id": "last_processed_post_number"})
    return metadata["value"] if metadata else 0

def update_last_processed_post_number(post_number):
    """Update the last processed post number in metadata."""
    metadata_collection.update_one(
        {"_id": "last_processed_post_number"},
        {"$set": {"value": post_number}},
        upsert=True
    )

def fetch_new_sentences(last_post_number):
    """Fetch new sentences with post_number greater than last processed post number."""
    query = {
        "post_number": {"$gt": last_post_number},
        "embedded flag": True,
        "process flag": True
    }
    return list(posts_collection.find(query))

def fetch_existing_sentences():
    """Fetch all existing sentences."""
    query = {
        "embedded flag": True,
        "process flag": True
    }
    return list(posts_collection.find(query))

def compute_cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def store_similarities(similarities):
    """Store computed similarities in the database."""
    if similarities:
        similarities_collection.insert_many(similarities)

def batch_job():
    # Step 1: Retrieve the last processed post number
    last_processed_post_number = fetch_last_processed_post_number()

    # Step 2: Fetch new sentences
    new_sentences = fetch_new_sentences(last_processed_post_number)
    if not new_sentences:
        print("No new sentences to process.")
        return

    # Step 3: Fetch existing sentences
    existing_sentences = fetch_existing_sentences()

    # Step 4: Compute similarities (avoid redundancy)
    similarities = []
    for new_sentence in new_sentences:
        for existing_sentence in existing_sentences:
            # Skip comparisons for the same user
            if new_sentence["user_id"] != existing_sentence["user_id"]:
                # Ensure consistent ordering to avoid redundant comparisons
                if new_sentence["post_number"] < existing_sentence["post_number"]:
                    similarity = compute_cosine_similarity(
                        new_sentence["embedded_text"], existing_sentence["embedded_text"]
                    )
                    similarities.append({
                        "sentence1_id": new_sentence["_id"],
                        "sentence2_id": existing_sentence["_id"],
                        "similarity": similarity,
                        "timestamp": datetime.utcnow()
                    })

    # Step 5: Store results
    store_similarities(similarities)

    # Step 6: Update the last processed post number
    max_post_number = max(sentence["post_number"] for sentence in new_sentences)
    update_last_processed_post_number(max_post_number)

# Run the batch job
batch_job()
