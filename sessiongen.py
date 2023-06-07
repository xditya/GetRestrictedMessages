from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(input("Enter API ID: "))
API_HASH = input("Enter API HASH: ")

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("Here is your session string:\n" + client.session.save())
