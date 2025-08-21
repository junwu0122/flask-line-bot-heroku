from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    TextSendMessage, PostbackEvent, MessageEvent, TextMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction
)
import os
from dotenv import load_dotenv
from stock_mongo import add_stock

load_dotenv()
app = Flask(__name__)

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
channel_secret = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

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
    text = event.message.text.strip()
    if text == "新增股票":
        buttons_template = ButtonsTemplate(
            title="新增股票",
            text="請選擇股票代碼",
            actions=[
                PostbackAction(label="2330", data="action=add_stock&stock=2330"),
                PostbackAction(label="2317", data="action=add_stock&stock=2317"),
                PostbackAction(label="2454", data="action=add_stock&stock=2454"),
            ]
        )
        template_message = TemplateSendMessage(
            alt_text="新增股票選單",
            template=buttons_template
        )
        line_bot_api.reply_message(event.reply_token, template_message)
    else:
        reply_text = f"大哥說的是: {text}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    if data.startswith("action=add_stock"):
        params = dict(param.split('=') for param in data.split('&'))
        stock_id = params.get('stock')

        price = 1000
        operator = 'less_than'

        add_stock(stock_id, price, operator)

        reply_text = f"已新增股票 {stock_id}，目標價格 {price}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run(port=8000)
