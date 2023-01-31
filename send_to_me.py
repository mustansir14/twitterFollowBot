import requests
import os
from dotenv import load_dotenv
load_dotenv()


def send_to_me(message):

    chat_ids = os.getenv("CHAT_IDS").split(",")

    for chat_id in chat_ids:
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage?chat_id={chat_id}&text={message}"
        res = requests.get(url)
        print(res.json())


if __name__ == "__main__":
    send_to_me("Testing")
