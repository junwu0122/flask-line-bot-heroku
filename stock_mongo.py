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
# 查詢某股票的最低價格（如果存在）
def get_stock():
    db = init_mongo_db()
    cursor = db.stock.find()
    return list(cursor)
def get_min_price(name):
    db = init_mongo_db()
    stocks_collection = db.prices

    result = stocks_collection.find_one({"stock_name": name})
    print("找尋股票")
    if result and "price" in result:
        return result["price"]
    else:
        return None
def add_stock(name, price,opertor="less_than"):
    db = init_mongo_db()
    prices = db.stock

    # 查找現有股票價格
    existing = prices.find_one({"stock_name": name})

    if existing is None:
        # 沒有資料，直接插入
        price_dic = {
            "stock_name": name,
            "price": price,
            "operator": opertor,
            "datetime": datetime.datetime.now(datetime.timezone.utc)
        }
        prices.insert_one(price_dic)
        print("資料不存在，已插入新資料並更新價格。")
    else:
        existing_price = existing.get("price")
        if existing_price is None or price < existing_price:
            # 新價格更便宜，更新資料
            new_values = {
                "$set": {
                    "price": price,
                    "datetime": datetime.datetime.now(datetime.timezone.utc)
                }
            }
            prices.update_one({"stock_name": name}, new_values)
            print("價格已更新為更低價格。")
        else:
            print("新價格沒有比現有價格低，未更新。")
def init_price(name,price):
    db = init_mongo_db()
    price_dic={
        "stock_name":name,
        "price": price,
        "datetime": datetime.datetime.now(datetime.timezone.utc)
    }
    prices = db.prices
    price_id = prices.insert_one(price_dic).inserted_id
    prices
    print("init success")

# add_stock("2330", 705)
# stocks = get_stock()
# print(stocks)
