from pymongo import MongoClient

def init_db():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['vehicle_data']
    collection = db['criminal_records']
    return collection

def check_criminal_record(collection, plate_number):
    record = collection.find_one({'plate_number': plate_number})
    return record if record else "No record found"

if __name__ == "__main__":
    collection = init_db()
    print(check_criminal_record(collection, "ABC1234"))
