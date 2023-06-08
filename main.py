# BoilerPlate Generated using https://github.com/xditya/TelethonSnippets Extension.
# Dependencies to be pre-installed:
# - telethon: Telegram Library.
# - python-decouple: To load config vars from .env files or environment variables.

# GetRestrictedMessagesBot - Telegram Bot to copy messages from chats with forward restrictions.
# Author: @xditya
# WebSite: https://xditya.me

import logging
import os

from decouple import config
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# initializing logger
logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
)
log = logging.getLogger("TelethonSnippets")

# fetching variales from env
try:
    API_ID = config("API_ID", cast=int)
    API_HASH = config("API_HASH")
    SESSION = config("SESSION")
    AUTHS = config("AUTHS")
except BaseException as ex:
    log.info(ex)

AUTH_USERS = [int(x) for x in AUTHS.split(" ")]

log.info("Connecting bot.")
try:
    client = TelegramClient(
        StringSession(SESSION), api_id=API_ID, api_hash=API_HASH
    ).start()
except BaseException as e:
    log.warning(e)
    exit(1)


# functions
@client.on(events.NewMessage(from_users=AUTH_USERS, func=lambda e: e.is_private))
async def on_new_link(event):
    text = event.text
    if not text:
        return

    # idk regex, lets do it the old way
    if not (text.startswith("https://t.me") or text.startswith("http://t.me")):
        return

    try:
        if "/c/" in text:
            chat_id = text.split("/c/")[1].split("/")[0]
            message_id = text.split("/c/")[1].split("/")[1]
        else:
            chat_id = text.split("/")[3]
            message_id = text.split("/")[4]
    except IndexError:
        return await event.reply("Invalid link?")

    if not message_id.isdigit():
        # message ids are always a number
        return await event.reply("Invalid link?")

    if chat_id.isdigit():
        peer = int(chat_id)
    elif chat_id.startswith("-100"):
        peer = int(chat_id)
    else:
        peer = chat_id

    try:
        message = await client.get_messages(peer, ids=int(message_id))
    except ValueError:
        return await event.reply(
            "I cant find the chat! Either it is invalid, or join it first from this account!"
        )
    except BaseException as e:
        return await event.reply(f"Error: {e}")

    if not message:
        return await event.reply("Message not found.")

    if message.media:
        reply_prog = await event.reply("Please wait, downloading media...")
        file = await message.download_media()
        await reply_prog.delete()
    else:
        file = None

    try:
        await client.send_message(event.chat_id, message.text, file=file)
    except ValueError:
        return await event.reply("Message has no text or media.")
    except BaseException as e:
        return await event.reply(f"Error: {e}")

    try:
        os.remove(file)
    except BaseException:
        pass


ubot_self = client.loop.run_until_complete(client.get_me())
log.info(
    "\nClient has started as %d.\n\nJoin @BotzHub [ https://t.me/BotzHub ] for more cool bots :)",
    ubot_self.id,
)
client.run_until_disconnected()
