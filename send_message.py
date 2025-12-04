# send_message.py
import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# Меняй это сообщение как хочешь
MESSAGE = "Дай детинцу витаминов"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
response = requests.post(url, json={
    "chat_id": CHAT_ID,
    "text": MESSAGE
})

if response.status_code == 200:
    print("✅ Сообщение отправлено!")
else:
    print("❌ Ошибка:", response.json())
