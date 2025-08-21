import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    PostbackEvent, TemplateSendMessage, ButtonsTemplate, PostbackAction
)
from dotenv import load_dotenv
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
    print("[LOG] 測試按鈕")
    buttons_template = ButtonsTemplate(
        title="測試選單",
        text="請先點按鈕試試",
        actions=[
            PostbackAction(label="A", data="testA"),
            PostbackAction(label="B", data="testB"),
        ]
    )
    template_message = TemplateSendMessage(
        alt_text="測試選單",  # 記得必填
        template=buttons_template
    )
    line_bot_api.reply_message(event.reply_token, template_message)

@handler.add(MessageEvent, message=TextMessage)
def handle_postback(event):
    data = event.postback.data
    if data.startswith("add_stock:"):
        stock_id = data.split(":")[1]
        # 模擬加股票（實際上你可呼叫 stock_mongo.add_stock）
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"✅ 已新增股票 {stock_id} 至監控清單")
        )
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(f"使用者輸入：{event.message.text}")
    if event.message.text == "新增股票":
        print("✅ 進入新增股票分支")

if __name__ == "__main__":
    app.run()
