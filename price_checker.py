import yfinance as yf
from stock_mongo import get_stock_by_name, update_notified_status, add_stock
from line_message import send_message  # 你的 LINE 發送函數

def get_current_price(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        data = ticker.history(period="1d")
        if data.empty:
            return None
        return float(data['Close'].iloc[-1])
    except Exception as e:
        print(f"取得 {stock_id} 價格失敗：{e}")
        return None

def check_price(stock):
    stock_id = stock["stock_name"]
    operator = stock.get("operator", "less_than")
    target_price = stock.get("price")
    notified = stock.get("notified", False)

    current_price = get_current_price(stock_id)
    if current_price is None:
        return

    send_msg = None
    if operator == "less_than":
        if current_price <= target_price and not notified:
            send_msg = f"{stock_id} 已低於 {target_price} 元，現價 {current_price}"
            update_notified_status(stock_id, True)
        elif current_price > target_price and notified:
            update_notified_status(stock_id, False)
    elif operator == "greater_than":
        if current_price >= target_price and not notified:
            send_msg = f"{stock_id} 已高於 {target_price} 元，現價 {current_price}"
            update_notified_status(stock_id, True)
        elif current_price < target_price and notified:
            update_notified_status(stock_id, False)

    if send_msg:
        send_message(send_msg)  # 發送 LINE 通知
        print(f"✅ 已發送通知: {send_msg}")
