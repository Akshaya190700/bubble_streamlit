from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Change as needed
db = client["bubble_db"]
users_collection = db['bubble_users']
posts_collection = db['bubble_posts']
cluster_collection=db['bubble_clusters']


# 2️⃣ Retrieve all sentence embeddings and IDs from MongoDB
embeddings = []
post_ids = []  # Store post IDs
cursor = posts_collection.find({}, {"_id": 1, "embedded_text": 1})  # Fetch IDs and embeddings

for doc in cursor:
    embeddings.append(np.array(doc["embedded_text"]))  # Convert stored list to NumPy array
    post_ids.append(doc["_id"])  # Store document ID

# Convert list of arrays to a NumPy matrix
embeddings = np.vstack(embeddings)  # Shape: (num_sentences, 768)

# 3️⃣ Dynamically Set max_k Based on Available Data
num_samples = embeddings.shape[0]
max_k = min(10, num_samples - 1)  # Ensures max_k < num_samples

# 4️⃣ Find Optimal K (Number of Clusters)
def optimal_k_silhouette(data, max_k):
    """Finds optimal K using the Silhouette Score."""
    best_k = 2
    best_score = -1

    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(data)
        score = silhouette_score(data, labels)

        if score > best_score:
            best_score = score
            best_k = k

    return best_k

def optimal_k_davies_bouldin(data, max_k):
    """Finds optimal K using Davies-Bouldin Index."""
    best_k = 2
    best_score = float("inf")

    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(data)
        score = davies_bouldin_score(data, labels)

        if score < best_score:
            best_score = score
            best_k = k

    return best_k

# Determine best K using multiple methods
best_k_silhouette = optimal_k_silhouette(embeddings, max_k=max_k)
best_k_davies = optimal_k_davies_bouldin(embeddings, max_k=max_k)

# Choose the most common/balanced K
optimal_k = (best_k_silhouette + best_k_davies) // 2  # Average them

# Output the optimal K values
print(f"Optimal K (Silhouette Score): {best_k_silhouette}")
print(f"Optimal K (Davies-Bouldin Index): {best_k_davies}")
print(f"Chosen Optimal K: {optimal_k}")

# Perform clustering with the chosen K
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(embeddings)

# 5️⃣ Store the clusters in a new collection in MongoDB
for post_id, label in zip(post_ids, cluster_labels):
    cluster_collection.update_one(
        {"_id": post_id},  # Match the original post by its ID
        {"$set": {"cluster_label": int(label)}},  # Convert numpy.int32 to Python int
        upsert=True  # If the post doesn't exist, create a new entry
    )

print(f"Clustering completed. Cluster labels stored in 'bubble_clusters' collection.")
