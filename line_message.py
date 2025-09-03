from dotenv import load_dotenv
import os
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.messaging.models import TextMessage, PushMessageRequest

# 載入環境變數
load_dotenv()

access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
user_id = os.getenv("LINE_USER_ID")

# 設定 API 金鑰
configuration = Configuration(access_token=access_token)

# 建立 API 實例並送出訊息
def send_message(response):
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        message = TextMessage(text=response)
        push_request = PushMessageRequest(to=user_id, messages=[message])
        messaging_api.push_message(push_message_request=push_request)
