from faker import Faker
from pymongo import MongoClient
import random
from datetime import datetime

# Initialize Faker and MongoDB client
faker = Faker()
# ConnectionString = "mongodb+srv://freego:freego%2322Monkey@freego-c0.y47x2e3.mongodb.net/user_recommendation?retryWrites=true&w=majority&serverSelectionTimeoutMS=30000&tls=true&tlsAllowInvalidCertificates=true"
# client = MongoClient(ConnectionString)
client = MongoClient("mongodb://localhost:27017/")
# Define database and collection
db = client["bubble_db"]
collection = db["bubble_users"]

# Generate dummy data
def generate_dummy_data(num_records):
    data = []
    for _ in range(num_records):
        name = faker.name()
        email = name.replace(" ", "").lower() + "@eplabs.com"
        document = {
            "name": name,
            "email": email,
            "password": "pw123",
            "age": random.randint(18, 80),
            "address": {
                "street": faker.street_address(),
                "city": faker.city(),
                "zip": faker.zipcode(),
            },
            "last_login_date": faker.date_time_this_decade(),
            "signup_date": datetime.now()
        }
        data.append(document)
    return data

# Insert dummy data into the collection
def insert_dummy_data(num_records):
    data = generate_dummy_data(num_records)
    collection.insert_many(data)
    print(f"Inserted {num_records} records into the collection.")

# Insert 23 records
insert_dummy_data(5)
