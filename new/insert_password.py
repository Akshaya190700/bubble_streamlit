from pymongo import MongoClient

# MongoDB connection
# ConnectionString = "mongodb+srv://freego:freego%2322Monkey@freego-c0.y47x2e3.mongodb.net/user_recommendation?retryWrites=true&w=majority&serverSelectionTimeoutMS=30000&tls=true&tlsAllowInvalidCertificates=true"
# client = MongoClient(ConnectionString)

client = MongoClient("mongodb://localhost:27017/")
db = client["bubble_db"]
users_collection = db['bubble_users']

# Update all documents to insert 'password' after 'email'
for document in users_collection.find():
    # Extract the _id to identify the document
    doc_id = document["_id"]
    
    # Create a new document structure with 'password' after 'email'
    updated_document = {}
    for key, value in document.items():
        updated_document[key] = value
        if key == "email":
            updated_document["password"] = "pw123"
    
    # Update the document in the collection
    users_collection.update_one({"_id": doc_id}, {"$set": updated_document})

print("Password field added to all documents.")
