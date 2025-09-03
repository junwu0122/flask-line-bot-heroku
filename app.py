import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    PostbackEvent, TemplateSendMessage, ButtonsTemplate, PostbackAction
)
from dotenv import load_dotenv
from stock_mongo import add_stock, get_stock_by_name

load_dotenv()

app = Flask(__name__)

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
channel_secret = os.getenv("LINE_CHANNEL_SECRET")
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# 暫存使用者狀態
# user_state[user_id] = {"stock_id": xxx, "operator": "less_than" or "greater_than", "step": 1/2/3}
user_state = {}

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text
    print(f"使用者({user_id})輸入：{text}")

    if user_id in user_state:
        state = user_state[user_id]

        if state["step"] == "waiting_price":
            try:
                price = float(text)
                add_stock(state["stock_id"], price, operator=state["operator"])
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"✅ 已新增股票 {state['stock_id']}，{ '低於' if state['operator']=='less_than' else '高於'} {price} 元")
                )
                del user_state[user_id]  # 清除暫存
            except ValueError:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ 請輸入數字格式的價格！")
                )
    elif text == "新增股票":
        # 顯示股票按鈕選單
        buttons_template = ButtonsTemplate(
            title="請選擇要新增的股票",
            text="點選下方按鈕新增：",
            actions=[
                PostbackAction(label="台積電 (2330)", data="choose_stock:2330"),
                PostbackAction(label="聯電 (2303)", data="choose_stock:2303"),
                PostbackAction(label="鴻海 (2317)", data="choose_stock:2317")
            ]
        )
        template_message = TemplateSendMessage(
            alt_text="新增股票選單",
            template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"你說的是: {text}")
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    data = event.postback.data

    if data.startswith("choose_stock:"):
        stock_id = data.split(":")[1]

        # 先檢查是否已存在
        if get_stock_by_name(stock_id):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"⚠️ 股票 {stock_id} 已在監控清單中")
            )
            return

        # 顯示 operator 選單
        buttons_template = ButtonsTemplate(
            title=f"{stock_id} 新增監控",
            text="請選擇比較方式：",
            actions=[
                PostbackAction(label="低於", data=f"choose_operator:{stock_id}:less_than"),
                PostbackAction(label="高於", data=f"choose_operator:{stock_id}:greater_than")
            ]
        )
        template_message = TemplateSendMessage(
            alt_text="選擇比較方式",
            template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)

    elif data.startswith("choose_operator:"):
        _, stock_id, operator = data.split(":")
        # 儲存暫存狀態，等待使用者輸入價格
        user_state[user_id] = {"stock_id": stock_id, "operator": operator, "step": "waiting_price"}
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"請輸入股票 {stock_id} 的目標價格：")
        )

if __name__ == "__main__":
    app.run(port=5000, debug=True)
