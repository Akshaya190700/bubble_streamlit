from pymongo import MongoClient
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["bubble_db"]
processed_collection = db["bubblebio_preproccesed"]
embedding_collection = db["bubblebio_embedding"]
clustered_collection = db["bubblebio_clusters"]
similarity_collection = db["bubblebio_similarity"]

# Load user embeddings
def load_embeddings():
    users = list(embedding_collection.find({}, {"_id": 1, "cluster": 1, "embedding": 1}))
    return users

# Compute cosine similarity within each cluster
def compute_similarity(users):
    clusters = {}
    
    # Group users by cluster
    for user in users:
        cluster_id = user["cluster"]
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(user)
    
    # Compute similarity per cluster
    results = []
    for cluster_id, cluster_users in clusters.items():
        embeddings = np.array([u["embedding"] for u in cluster_users])
        user_ids = [u["_id"] for u in cluster_users]
        
        if len(embeddings) < 2:
            continue  # Skip clusters with only one user
        
        sim_matrix = cosine_similarity(embeddings)
        
        for i, user_id in enumerate(user_ids):
            similar_users = [(user_ids[j], float(sim_matrix[i, j])) for j in range(len(user_ids)) if i != j]
            similar_users.sort(key=lambda x: x[1], reverse=True)  # Sort by similarity
            results.append({"user_id": user_id, "similar_users": similar_users[:5]})  # Top 5 similar users
    
    return results

# Store results in MongoDB
def store_results(results):
    similarity_collection.delete_many({})  # Clear existing data
    similarity_collection.insert_many(results)
    print("Similarity data stored successfully!")

# Run the pipeline
users = load_embeddings()
results = compute_similarity(users)
store_results(results)
