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

# 取得所有監控的股票
def get_stock():
    db = init_mongo_db()
    cursor = db[COLLECTION_NAME].find(
        {},  # 條件為空，取全部
        {"_id": 0, "stock_name": 1, "price": 1, "operator": 1, "notified": 1, "datetime": 1}
    )
    return list(cursor)

# 查詢某股票的監控設定
def get_stock_info(name):
    db = init_mongo_db()
    stocks_collection = db[COLLECTION_NAME]
    result = stocks_collection.find_one({"stock_name": name})
    return result

# 查詢某股票的監控價格
def get_target_price(name):
    stock = get_stock_info(name)
    if stock and "price" in stock:
        return stock["price"]
    else:
        return None

# 查詢某股票的監控條件 (less_than / greater_than)
def get_operator(name):
    stock = get_stock_info(name)
    if stock and "operator" in stock:
        return stock["operator"]
    else:
        return "less_than"  # 預設

# 新增或更新股票監控價
def add_stock(name, price, operator="less_than"):
    if operator not in ["less_than", "greater_than"]:
        raise ValueError("❌ operator 只能是 'less_than' 或 'greater_than'")

    db = init_mongo_db()
    stocks = db[COLLECTION_NAME]

    existing = stocks.find_one({"stock_name": name})

    if existing is None:
        # 沒有資料，直接插入
        price_dic = {
            "stock_name": name,
            "price": price,
            "operator": operator,
            "notified": False,  # ✅ 初始化通知狀態
            "datetime": datetime.datetime.now(datetime.timezone.utc)
        }
        stocks.insert_one(price_dic)
        print(f"✅ 已新增股票監控：{name}, {operator} {price}")
    else:
        # 覆蓋更新並重置通知狀態
        new_values = {
            "$set": {
                "price": price,
                "operator": operator,
                "notified": False,  # ✅ 更新監控時重置
                "datetime": datetime.datetime.now(datetime.timezone.utc)
            }
        }
        stocks.update_one({"stock_name": name}, new_values)
        print(f"🔄 已更新股票監控：{name}, {operator} {price}")

def get_stock_by_name(name):
    db = init_mongo_db()
    return db[COLLECTION_NAME].find_one({"stock_name": name})


def update_notified_status(name, status: bool):
    db = init_mongo_db()
    db[COLLECTION_NAME].update_one(
        {"stock_name": name},
        {"$set": {"notified": status}}
    )
