from pymongo import MongoClient
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from collections import defaultdict

client = MongoClient("mongodb://localhost:27017/")
db = client["bubble_db"]
users_collection = db['bubble_users']
posts_collection = db['bubble_posts']
cluster_posts_collection = db["bubble_clusters"]


# Step 3: Fetch posts from the posts collection
posts = list(posts_collection.find({}))  # Assuming you're fetching all posts

# Step 4: Extract pre-embedded vectors and corresponding user IDs
post_embeddings = [post["embedded_text"] for post in posts]  # Assuming "embedded_text" stores the pre-processed embeddings
user_ids = [str(post["user_id"]) for post in posts]


# Step 5: Use DBSCAN for clustering
scaler = StandardScaler()
post_embeddings_scaled = scaler.fit_transform(post_embeddings)

# Set DBSCAN parameters (you can adjust these values based on your data)
dbscan = DBSCAN(eps=0.5, min_samples=3, metric='cosine')
clusters = dbscan.fit_predict(post_embeddings_scaled)

# Step 6: Group users by clusters
user_groups = defaultdict(list)
for user_id, cluster_label in zip(user_ids, clusters):
    if cluster_label != -1:  # -1 indicates noise points in DBSCAN
        user_groups[cluster_label].append(user_id)

# Step 7: Insert the clustered posts into the new 'cluster_posts' collection
for post, cluster_label in zip(posts, clusters):
    # Create the new post document with the cluster label
    cluster_post = post.copy()  # Make a copy of the post to add the cluster information
    cluster_post["cluster_label"] = int(cluster_label)  # Add cluster label
    
    # Insert the document into the 'cluster_posts' collection
    cluster_posts_collection.insert_one(cluster_post)

# Step 8: Display results
print("User Groups based on DBSCAN Clustering")
for cluster, users in user_groups.items():
    print(f"Cluster {cluster}: Users {users}")