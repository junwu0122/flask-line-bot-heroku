from linebot import LineBotApi
from linebot.models import TextSendMessage
import os
from dotenv import load_dotenv

load_dotenv()
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def send_message(text, user_id=None):
    if user_id:
        line_bot_api.push_message(user_id, TextSendMessage(text=text))
    else:
        print(f"[DEBUG] {text}")
