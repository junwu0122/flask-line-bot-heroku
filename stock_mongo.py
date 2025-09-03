import os
from dotenv import load_dotenv
from pymongo import MongoClient
import datetime

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL")
database_name = 'Jun'
COLLECTION_NAME = 'stock'

def init_mongo_db():
    client = MongoClient(MONGO_URL)
    db = client[database_name]
    return db

def get_stock():
    db = init_mongo_db()
    cursor = db[COLLECTION_NAME].find(
        {}, 
        {"_id":0, "stock_name":1, "price":1, "operator":1, "notified":1, "datetime":1}
    )
    return list(cursor)

def get_stock_by_name(name):
    db = init_mongo_db()
    return db[COLLECTION_NAME].find_one({"stock_name": name})

def add_stock(name, price, operator="less_than"):
    if operator not in ["less_than", "greater_than"]:
        raise ValueError("operator 只能是 'less_than' 或 'greater_than'")

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
        print(f"✅ 已新增股票監控：{name}, {operator} {price}")
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
        print(f"🔄 已更新股票監控：{name}, {operator} {price}")

def update_notified_status(name, status: bool):
    db = init_mongo_db()
    db[COLLECTION_NAME].update_one(
        {"stock_name": name},
        {"$set": {"notified": status}}
    )
