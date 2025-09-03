import yfinance as yf
from line_message import send_message
from stock_mongo import add_stock, update_notified_status, get_stock_by_name

def get_current_price(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        data = ticker.history(period="1d")

        if data.empty:
            raise ValueError("查無報價資料")

        current_price = data['Close'].iloc[-1]
        return float(current_price)

    except Exception as e:
        print(f"取得 {stock_id} 價格失敗：{e}")
        return None


def check_price(stock_id, operator='less_than', price=1200):
    current_price = get_current_price(stock_id)

    if current_price is None:
        print(f"無法取得 {stock_id} 的價格")
        return

    print(f"{stock_id} 當前價格: {current_price}")

    stock = get_stock_by_name(stock_id)  # 取 DB 裡的紀錄
    already_notified = stock.get("notified", False) if stock else False

    if operator == 'less_than':
        if current_price <= price:
            if not already_notified:
                print("✅ 低於或等於目標價格，發送通知")
                add_stock(stock_id, price, operator="less_than")
                send_message(f"📉 {stock_id} 已低於 {price} 元，現在價格為 {current_price}")
                update_notified_status(stock_id, True)  # ✅ 標記已通知
        else:
            if already_notified:
                print("🔄 價格回升，重置通知狀態")
                update_notified_status(stock_id, False)

    elif operator == 'greater_than':
        if current_price >= price:
            if not already_notified:
                print("✅ 高於或等於目標價格，發送通知")
                add_stock(stock_id, price, operator="greater_than")
                send_message(f"📈 {stock_id} 已高於 {price} 元，現在價格為 {current_price}")
                update_notified_status(stock_id, True)  # ✅ 標記已通知
        else:
            if already_notified:
                print("🔄 價格回落，重置通知狀態")
                update_notified_status(stock_id, False)

    else:
        print(f"❗ 不支援的比較方式：{operator}")
