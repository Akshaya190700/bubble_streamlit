import json
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # MongoDB connection string
db = client["bubble_db"]  # Your database name
source_collection = db["bubble_users"]  # Collection where the user data is stored
collection = db["bubblebio_preproccesed"]  # New collection for processed data

# Function to flatten user data
def flatten_user_data(user):
    text_data = []
    
    # Basic details
    text_data.append(f"Job Specialization: {user.get('job_specialization', '')}")
    text_data.append(f"Domain: {user.get('domain', '')}")
    text_data.append(f"Profile Bio: {user.get('profile_bio', '')}")

    # Skills
    skills = user.get("skills", {})
    for category, skillset in skills.items():
        if isinstance(skillset, dict):
            for subcategory, values in skillset.items():
                if isinstance(values, list):
                    text_data.extend(values)
                else:
                    text_data.append(f"{subcategory}: {values}")
        else:
            text_data.append(str(skillset))

    # Interests & Hobbies
    interests = user.get("interests", {})
    for category, values in interests.items():
        text_data.extend(values)
    text_data.extend(user.get("hobbies", []))

    # Language Proficiency
    lang_prof = user.get("language_proficiency", {})
    for category, languages in lang_prof.items():
        text_data.extend(languages)

    # Extended Details
    extended_details = user.get("extended_details", {})
    for key, value in extended_details.items():
        if isinstance(value, list):
            text_data.extend(value)
        else:
            text_data.append(str(value))

    return " | ".join(text_data)

# Process all users from the source collection
users = source_collection.find({})
processed_users = {}

for user in users:
    user_id = str(user["_id"])
    processed_data = flatten_user_data(user)
    
    # Insert or update processed data in the new collection
    collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"processed_data": processed_data}},
        upsert=True  # Ensures the document is created if it doesn't exist
    )

# Print a success message after all users are processed
print("User data preprocessed successfully.")
