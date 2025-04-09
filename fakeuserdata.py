from faker import Faker
from pymongo import MongoClient
import random

# Initialize Faker and MongoDB client
faker = Faker()
client = MongoClient("mongodb://localhost:27017/")

# Define database and collection
db = client["user_db"]
collection = db["users"]

# Generate dummy data
def generate_dummy_data(num_records):
    data = []
    for _ in range(num_records):
        document = {
            "name": faker.name(),
            "email": faker.email(),
            "password": "pw123",
            "age": random.randint(18, 80),
            "address": {
                "street": faker.street_address(),
                "city": faker.city(),
                "zip": faker.zipcode(),
            },
            "is_active": faker.boolean(),
            "signup_date": faker.date_time_this_decade(),
        }
        data.append(document)
    return data

# Insert dummy data into the collection
def insert_dummy_data(num_records):
    data = generate_dummy_data(num_records)
    collection.insert_many(data)
    print(f"Inserted {num_records} records into the collection.")

# Insert 100 records
insert_dummy_data(20)