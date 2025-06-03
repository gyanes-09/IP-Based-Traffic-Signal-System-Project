from pymongo import MongoClient
import json

def initialize_db():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['vehicle_data']
    collection = db['criminal_records']

    # Load sample data
    with open('database/criminal_records.json', 'r') as file:
        records = json.load(file)
        collection.insert_many(records)

    print("Database initialized with sample records.")

if __name__ == "__main__":
    initialize_db()
