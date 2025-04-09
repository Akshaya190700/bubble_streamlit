from pymongo import MongoClient
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["bubble_db"]  # Use the bubble_db database
users_collection = db["bubble_users"]  # User data collection
posts_collection = db["bubble_posts"]  # Post collection for sentences

# Load pre-trained model and tokenizer
MODEL_NAME = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
bert_model = AutoModel.from_pretrained(MODEL_NAME)

# Function to compute embeddings for text
def get_embedding(text, tokenizer, model):
    tokens = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)
    input_ids, attention_mask = tokens["input_ids"], tokens["attention_mask"]
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    cls_embedding = outputs.last_hidden_state[:, 0, :]  # CLS token
    return cls_embedding.squeeze(0).cpu().numpy()

# Function to calculate similarity for each field
def calculate_field_similarity(user_sentence, profile_data, field, tokenizer, model):
    user_embedding = get_embedding(user_sentence, tokenizer, model)
    profile_field_value = profile_data.get(field, "")
    if isinstance(profile_field_value, list):
        profile_text = " ".join(profile_field_value)  # Concatenate list elements into a single string
    else:
        profile_text = profile_field_value
    profile_embedding = get_embedding(profile_text, tokenizer, model)
    return cosine_similarity(user_embedding.reshape(1, -1), profile_embedding.reshape(1, -1))[0][0]

# Function to calculate overall similarity
def calculate_overall_similarity(user_sentence, profile_data, fields, tokenizer, model, field_weights=None):
    field_weights = field_weights or {field: 1.0 for field in fields}  # Default equal weights if not provided
    total_weight = sum(field_weights.values())
    overall_similarity = 0.0
    for field in fields:
        similarity = calculate_field_similarity(user_sentence, profile_data, field, tokenizer, model)
        overall_similarity += field_weights.get(field, 1.0) * similarity
    overall_similarity /= total_weight
    return overall_similarity

# Fetch all users from MongoDB
all_users = list(users_collection.find())

# Fields to compare and their weights
fields_to_check = [
    "profile_bio",
    "interests",
    "occupation",
    "job_specialization",
    "domain",
    "skills",
    "events_interested_in",
    "bucket_list_items"
]
field_weights = {
    "profile_bio": 1.0,
    "interests": 1.0,
    "occupation": 1.0,
    "job_specialization": 1.0,
    "domain": 1.0,
    "skills": 1.5,
    "events_interested_in": 1.0,
    "bucket_list_items": 1.0
}

# Matchmaking
matches = []
for user_a in all_users:
    user_a_id = user_a["_id"]
    user_a_sentence = ""
    
    # Retrieve the latest post (sentence) of user A from posts collection
    user_a_post = posts_collection.find_one({"user_id": user_a_id}, sort=[("date_posted", -1)])  # Assuming `date_posted` field is used
    if user_a_post:
        user_a_sentence = user_a_post.get("content", "")
    
    user_a_profile = {key: user_a.get(key, "") for key in fields_to_check}

    for user_b in all_users:
        user_b_id = user_b["_id"]
        if user_a_id == user_b_id:
            continue  # Skip matching the same user

        user_b_profile = {key: user_b.get(key, "") for key in fields_to_check}
        similarity_score = calculate_overall_similarity(
            user_a_sentence, user_b_profile, fields_to_check, tokenizer, bert_model, field_weights
        )
        matches.append({
            "user_a_id": user_a_id,
            "user_b_id": user_b_id,
            "similarity_score": similarity_score
        })

# Sort matches by similarity score
matches = sorted(matches, key=lambda x: x["similarity_score"], reverse=True)

# Output top matches
for match in matches[:10]:  # Show top 10 matches
    print(f"User A (ID: {match['user_a_id']}) matches with User B (ID: {match['user_b_id']}) with similarity score: {match['similarity_score']:.4f}")


