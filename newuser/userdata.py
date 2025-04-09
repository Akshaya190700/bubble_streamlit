from pymongo import MongoClient
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["user_recommendation_db"]  # Replace with your database name
user_collection = db["user_profiles"]  # Replace with your collection name

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
    field_similarities = {}
    for field in fields:
        similarity = calculate_field_similarity(user_sentence, profile_data, field, tokenizer, model)
        field_similarities[field] = similarity
        overall_similarity += field_weights[field] * similarity
    overall_similarity /= total_weight
    return overall_similarity, field_similarities

# Fetch data from MongoDB
user_id = "12345"  # Replace with the target user's ID
user_data = user_collection.find_one({"_id": user_id})

# Extract the user sentence and profile
user_sentence = user_data.get("user_sentence", "")
profile = user_data.get("profile", {})

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
    "profile_bio": 2.0,  # Assign higher weight to profile bio if it is more important
    "interests": 1.0,
    "occupation": 1.0,
    "job_specialization": 1.0,
    "domain": 1.0,
    "skills": 1.5,
    "events_interested_in": 0.8,
    "bucket_list_items": 0.5
}

# Calculate overall similarity and field-wise similarities
overall_similarity, field_similarities = calculate_overall_similarity(
    user_sentence, profile, fields_to_check, tokenizer, bert_model, field_weights
)

# Output results
print(f"Overall Similarity Score: {overall_similarity:.4f}")
print("Field-wise Similarity Scores:")
for field, score in field_similarities.items():
    print(f"  {field}: {score:.4f}")
