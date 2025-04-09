import torch
from transformers import AutoTokenizer, AutoModel
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # MongoDB connection string
db = client["bubble_db"]  # Your database name
processed_collection = db["bubblebio_preproccesed"]  # Collection with preprocessed data
embedding_collection = db["bubblebio_embedding"]  # New collection to store embeddings

# Load pre-trained model and tokenizer from Hugging Face
model_name = "sentence-transformers/all-distilroberta-v1"  # Corrected model name
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Function to generate embeddings from text using the pre-trained model
def generate_embedding(text):
    # Tokenize input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    
    # Forward pass through the model
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get embeddings from the last hidden state (pool the token embeddings)
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()  # Mean pooling
    
    return embeddings.numpy().tolist()  # Convert to list for MongoDB storage

# Process all preprocessed users and generate embeddings
users = processed_collection.find({})
for user in users:
    user_id = str(user["_id"])
    processed_data = user.get("processed_data", "")
    
    if processed_data:
        # Generate embedding for the preprocessed data
        embedding = generate_embedding(processed_data)
        
        # Insert or update the embedding in MongoDB
        embedding_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"embedding": embedding}},
            upsert=True  # Insert if not exists
        )

print("Embeddings for preprocessed data stored successfully.")
