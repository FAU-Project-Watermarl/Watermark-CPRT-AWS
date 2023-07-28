from pymongo.mongo_client import MongoClient
import certifi
import ErrorHandling
from pymongo.errors import PyMongoError
from datetime import datetime

db_name = "watermark"
collection_name = "uuid"
uri = "mongodb+srv://mark:mark@cluster0.82o4qbt.mongodb.net/?retryWrites=true&w=majority"

client = None
db = None
collection = None

def open_db(custom_db=None, custom_collection=None):
    global client, db, collection

    client = MongoClient(uri, tlsCAFile=certifi.where())
    selected_db_name = db_name
    selected_collection_name = collection_name
    if(custom_db):
        selected_db_name = custom_db
    if(custom_collection):
        selected_collection_name = custom_collection

    try:
        client.admin.command('ping')
        db = client[selected_db_name]
        collection = db[selected_collection_name]
        print("successfully connected to MongoDB!")

    except PyMongoError as e:
        ErrorHandling.error_handling_format(str(e))

def close_db():
    try:
        client.close()
        print("successfully closed connection!")

    except PyMongoError as e:
        ErrorHandling.error_handling_format(str(e))

def check_stored_uuid(value):
    try:
        result = collection.find_one({'_id': value})

        if result is None:
            return False
        else:
            return True
    except PyMongoError as e:
        ErrorHandling.error_handling_format(str(e))
        
#inserts into db json some value
def insert_uuid_value(uuid, dash_obj):
    
    str_url = f'https://d6p5bgq5sl2je.cloudfront.net/{dash_obj["bucket_filename"]}/{uuid}/{dash_obj["manifest_output_nested_path"]}'

    try:
        timestamp = datetime.now()
        print("Timestamp:", timestamp)
        print("Associated Url for validation:",  str_url)
        collection.insert_one( 
        {
        "_id":uuid,
        "time_stamp":timestamp, 
        "validation_url_link":str_url
        })
    except PyMongoError as e:
        ErrorHandling.error_handling_format(str(e))

