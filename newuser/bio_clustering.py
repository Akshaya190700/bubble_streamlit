import numpy as np
from pymongo import MongoClient
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# 🔹 Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Update your MongoDB details
db = client["bubble_db"]  # Replace with your database name
embedding_collection = db["bubblebio_embedding"]  # Collection with stored embeddings
clustered_collection = db["bubblebio_clusters"]  # Collection to store clustered results

# 🔹 Retrieve Embeddings
users = list(embedding_collection.find({}))
user_ids = [str(user["_id"]) for user in users]  # Use _id as user identifier
embeddings = np.array([user["embedding"] for user in users])  # Convert to NumPy array

# 🔹 Determine Best k (Elbow & Silhouette)
def find_best_k(embeddings, min_k=2, max_k=10):
    best_k = min_k
    best_score = -1
    
    for k in range(min_k, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        score = silhouette_score(embeddings, labels)  # Compute silhouette score
        
        if score > best_score:
            best_score = score
            best_k = k

    print(f"Best k found: {best_k}")
    return best_k

best_k = find_best_k(embeddings)

# 🔹 Apply KMeans Clustering
kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(embeddings)

# 🔹 Store Clustered Data in MongoDB
for i, user_id in enumerate(user_ids):
    clustered_collection.insert_one({
        "_id": user_id,  # Use _id as the identifier for the user
        "cluster": int(cluster_labels[i])
    })

print(f"✅ Clustering done! {len(user_ids)} users assigned to {best_k} clusters.")
