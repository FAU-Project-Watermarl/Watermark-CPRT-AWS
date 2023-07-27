from pymongo.mongo_client import MongoClient
import certifi
import ErrorHandling
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from datetime import datetime

db_name = "watermark"
collection_name = "uuid"

client = None
db = None
collection = None

def open_db(custom_db=None, custom_collection=None):
    global client, db, collection

    uri = "mongodb+srv://mark:mark@cluster0.82o4qbt.mongodb.net/?retryWrites=true&w=majority"
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

    except Exception as e:
        ErrorHandling.error_handling_format(e)

def close_db():
    try:
        client.close()
        print("successfully closed connection!")

    except Exception as e:
        ErrorHandling.error_handling_format(e)

def check_stored_uuid(value):
    try:
        result = collection.find_one({'_id': value})

        if result is None:
            return False
        else:
            return True
    except Exception as e:
        ErrorHandling.error_handling_format(e)
        
#inserts into db json some value
def insert_uuid_value(uuid, dash_obj):
    
    str = f'https://d6p5bgq5sl2je.cloudfront.net/{dash_obj["bucket_filename"]}/{uuid}/{dash_obj["manifest_output_nested_path"]}'

    try:
        timestamp = datetime.now()  
        collection.insert_one( 
        {
        "_id":uuid,
        "time_stamp":timestamp, 
        "validation_url_link":str
        })
    except Exception as e:
        ErrorHandling.error_handling_format(e)

