import os
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

def send_message(text, user_id=None):
    """
    發送 LINE 訊息。
    如果 user_id 提供，則使用 push_message；否則只 debug 印出。
    """
    if user_id:
        line_bot_api.push_message(user_id, TextSendMessage(text=text))
    else:
        print(f"[DEBUG] LINE 訊息: {text}")
