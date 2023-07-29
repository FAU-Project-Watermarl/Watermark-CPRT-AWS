from pymongo.mongo_client import MongoClient
import certifi
import ErrorHandling
import os
from pymongo.errors import PyMongoError
from datetime import datetime
import dotenv
from dotenv import load_dotenv

 # outputs "value"

db_name = "watermark"
collection_name = "uuid"
env_file_name = "MongoCredentials.env"

client = None
db = None
collection = None

def open_db(custom_db=None, custom_collection=None):
    global client, db, collection

    dotenv_path = f"{os.getcwd()}/{env_file_name}"
    load_dotenv(dotenv_path)
    uri = os.getenv("MONGODB_URI")
    if(uri == None):
        ErrorHandling.error_handling_format("Unable to get uri credentials from env")
        
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
def insert_uuid_value(dash_obj):
    
    str_url = f'https://d6p5bgq5sl2je.cloudfront.net/{dash_obj["bucket_filename"]}/{dash_obj["uuid_value"]}/{dash_obj["manifest_output_nested_path"]}'

    try:
        timestamp = datetime.now()
        print("Timestamp:", timestamp)
        print("Associated Url for validation:",  str_url)
        collection.insert_one( 
        {
        "_id":dash_obj["uuid_value"],
        "time_stamp":timestamp, 
        "validation_url_link":str_url
        })
    except PyMongoError as e:
        ErrorHandling.error_handling_format(str(e))

