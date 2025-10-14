# BoilerPlate Generated using https://github.com/xditya/TelethonSnippets Extension.
# Modified by ChatGPT (GPT-5) to support BOT_TOKEN-based startup.

import logging
import os
from decouple import config
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ================== Logger Setup ==================
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s")
log = logging.getLogger("TelethonBot")

# ================== Config Vars ==================
try:
    API_ID = config("API_ID", cast=int)
    API_HASH = config("API_HASH")
    SESSION = config("SESSION", default=None)
    BOT_TOKEN = config("BOT_TOKEN", default=None)
    AUTHS = config("AUTHS", default="")  # space separated user IDs
except BaseException as ex:
    log.error("Error loading environment variables: %s", ex)
    exit(1)

AUTH_USERS = [int(x) for x in AUTHS.split()] if AUTHS else []

# ================== Client Setup ==================
log.info("Connecting to Telegram...")

try:
    if BOT_TOKEN:
        client = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
        log.info("Started in BOT mode ✅")
    elif SESSION:
        client = TelegramClient(StringSession(SESSION), API_ID, API_HASH).start()
        log.info("Started in USERBOT mode ✅")
    else:
        log.error("No SESSION or BOT_TOKEN provided. Please set one of them.")
        exit(1)
except Exception as e:
    log.error("Client start failed: %s", e)
    exit(1)

# ================== Core Function ==================
@client.on(events.NewMessage(from_users=AUTH_USERS))
async def on_new_link(event):
    text = event.text
    if not text:
        return

    if not (text.startswith("https://t.me") or text.startswith("http://t.me")):
        return

    try:
        parts = text.replace("https://", "").replace("http://", "").split("/")
        chat_id = parts[2 if parts[1] in ["c", "s"] else 1]
        message_id = parts[-1]
    except IndexError:
        return await event.reply("⚠️ Invalid link format!")

    if not message_id.isdigit():
        return await event.reply("⚠️ Invalid message ID!")

    peer = int(chat_id) if chat_id.isdigit() or chat_id.startswith("-100") else chat_id

    try:
        message = await client.get_messages(peer, ids=int(message_id))
    except Exception as e:
        return await event.reply(f"❌ Error fetching message:\n`{e}`")

    if not message:
        return await event.reply("⚠️ Message not found!")

    file = None
    if message.media:
        reply_prog = await event.reply("📥 Downloading media...")
        file = await message.download_media()
        await reply_prog.delete()

    try:
        await client.send_message(event.chat_id, message.text or "", file=file)
    except Exception as e:
        await event.reply(f"⚠️ Failed to send message:\n`{e}`")

    if file:
        try:
            os.remove(file)
        except Exception:
            pass

# ================== Start Message ==================
async def main():
    me = await client.get_me()
    log.info(f"✅ Bot started as {me.first_name} (ID: {me.id})")
    await client.send_message(
        me.id,
        f"🤖 **Bot Started!**\n\nID: `{me.id}`\nMode: `{'BOT' if BOT_TOKEN else 'USERBOT'}`"
    )

client.loop.run_until_complete(main())
client.run_until_disconnected()
