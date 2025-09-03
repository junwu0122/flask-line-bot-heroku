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
    print(f"使用者輸入：{event.message.text}")
    if event.message.text == "新增股票":
        print("✅ 進入新增股票分支")
        buttons_template = ButtonsTemplate(
            title="請選擇要新增的股票",
            text="點選下方按鈕新增：",
            actions=[
                PostbackAction(label="台積電 (2330)", data="add_stock:2330"),
                PostbackAction(label="聯電 (2303)", data="add_stock:2303"),
                PostbackAction(label="鴻海 (2317)", data="add_stock:2317")
            ]
        )
        template_message = TemplateSendMessage(
            alt_text="新增股票選單",
            template=buttons_template
        )
        print("準備回覆按鈕選單訊息")
        try:
            line_bot_api.reply_message(event.reply_token, template_message)
            print("已呼叫 reply_message")
        except Exception as e:
            print(f"發生錯誤: {e}")
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"你說的是: {event.message.text}")
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    if data.startswith("add_stock:"):
        stock_id = data.split(":")[1]
        # 模擬加股票（實際上你可呼叫 stock_mongo.add_stock）
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"✅ 已新增股票 {stock_id} 至監控清單")
        )

if __name__ == "__main__":
    app.run()
