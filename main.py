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
except BaseException as ex:
    log.info(ex)


log.info("Connecting bot.")
try:
    client = TelegramClient(
        StringSession(SESSION), api_id=API_ID, api_hash=API_HASH
    ).start()
except BaseException as e:
    log.warning(e)
    exit(1)


# functions
@client.on(events.NewMessage(
    outgoing=True,
    pattern=r"^.getmsg"))
async def on_new_link(event):
    await event.edit("`Checking the link...`")
    async def download_progress(current, total):
        percentage = round(
            current / total * 100, 2)
        progress = "[{}{}] {}%".format(
            "▰" * int(percentage / 10),
            "▱" * (10 - int(percentage / 10)),
            percentage)
        await event.edit(
            "`Downloading media...`\n"
            f"\n`{progress}`"
            )
    async def upload_progress(current, total):
        percentage = round(
            current / total * 100, 2)
        progress = "[{}{}] {}%".format(
            "▱" * int(percentage / 10),
            "▰" * (10 - int(percentage / 10)),
            percentage)
        await event.edit(
            "`The media has been downloaded.`\n"
            "`Sending media...`\n"
            f"\n`{progress}`"
            )
    text = event.text.strip()
    if len(text.split()) != 2:
        await event.edit(
            "`Invalid command format.`"
            "\n**Usage:** `.getmsg <link>`")
        return
    link = text.split()[1]
    if not (link.startswith("https://t.me") or link.startswith("http://t.me")):
        await event.edit("`Invalid link?`")
        return
    try:
        if "/c/" in link:
            chat_id = link.split("/c/")[1].split("/")[0]
            message_id = link.split("/c/")[1].split("/")[1]
        else:
            chat_id = link.split("/")[3]
            message_id = link.split("/")[4]
    except IndexError:
        return await event.edit("`Invalid link?`")

    if not message_id.isdigit():
        return await event.edit("`Invalid link?`")

    if chat_id.isdigit():
        peer = int(chat_id)
    elif chat_id.startswith("-100"):
        peer = int(chat_id)
    else:
        peer = chat_id

    try:
        message = await client.get_messages(peer, ids=int(message_id))
    except ValueError:
        return await event.edit(
            "`I cant find the chat! Either it is invalid, or join it first from this account!`"
        )
    except BaseException as e:
        return await event.edit(f"**Error:** `{e}`")

    if not message:
        return await event.edit("`Message not found.`")

    file = None
    if message.media:
        file = await message.download_media(
            progress_callback=download_progress)
    try:
        if file:
            await client.send_file(
                event.chat_id,
                file,
                caption=message.text,
                progress_callback=upload_progress)
        else:
            await client.send_message(
                event.chat_id,
                message.text)
        await event.delete()
    except ValueError:
        await event.edit(
            "`Message has no text or media.`")
        return
    except BaseException as e:
        return await event.edit(
            f"**Error:** `{e}`")
    finally:
        try:
            if file:
                os.remove(file)
        except Exception:
            pass


ubot_self = client.loop.run_until_complete(client.get_me())
log.info(
    "\nClient has started as %d.\n\nJoin @BotzHub [ https://t.me/BotzHub ] for more cool bots :)",
    ubot_self.id,
)
client.run_until_disconnected()