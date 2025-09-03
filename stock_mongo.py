import os
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = 'Jun'
COLLECTION_NAME = 'stock'

def init_mongo_db():
    client = MongoClient(MONGO_URL)
    db = client[DATABASE_NAME]
    return db

def get_stock():
    db = init_mongo_db()
    return list(db[COLLECTION_NAME].find({}))

def get_stock_by_name(name):
    db = init_mongo_db()
    return db[COLLECTION_NAME].find_one({"stock_name": name})

def add_stock(name, price, operator="less_than"):
    if operator not in ["less_than", "greater_than"]:
        raise ValueError("operator 只能是 less_than 或 greater_than")
    db = init_mongo_db()
    stocks = db[COLLECTION_NAME]
    existing = stocks.find_one({"stock_name": name})

    if existing is None:
        price_dic = {
            "stock_name": name,
            "price": price,
            "operator": operator,
            "notified": False,
            "datetime": datetime.datetime.now(datetime.timezone.utc)
        }
        stocks.insert_one(price_dic)
    else:
        new_values = {
            "$set": {
                "price": price,
                "operator": operator,
                "notified": False,
                "datetime": datetime.datetime.now(datetime.timezone.utc)
            }
        }
        stocks.update_one({"stock_name": name}, new_values)

def update_notified_status(name, status: bool):
    db = init_mongo_db()
    db[COLLECTION_NAME].update_one(
        {"stock_name": name},
        {"$set": {"notified": status}}
    )
