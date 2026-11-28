# BoilerPlate Generated using https://github.com/xditya/TelethonSnippets Extension.
# Dependencies to be pre-installed:
# - telethon: Telegram Library.
# - python-decouple: To load config vars from .env files or environment variables.

# GetRestrictedMessagesBot - Telegram Bot to copy messages from chats with forward restrictions.
# Author: @xditya
# WebSite: https://xditya.me

import asyncio
import logging
import re
import struct
from tempfile import TemporaryDirectory
from urllib.parse import parse_qsl, urlsplit

from decouple import config
from telethon import TelegramClient, errors, events, types
from telethon.sessions import StringSession

log = logging.getLogger(__name__)
POST_PATH = re.compile(
    r"/(?:c/(?P<channel>[1-9][0-9]{0,18})|(?:s/)?(?P<username>[A-Za-z][A-Za-z0-9_]*))"
    r"/(?:(?P<topic>[1-9][0-9]{0,9})/)?(?P<post>[1-9][0-9]{0,9})/?"
)


def required(name):
    value = config(name, default="").strip()
    if not value:
        raise ValueError(f"Set {name} in the environment or .env file.")
    return value


def load_settings():
    api_id = required("API_ID")
    if not re.fullmatch(r"[1-9][0-9]{0,9}", api_id) or int(api_id) >= 2**31:
        raise ValueError("API_ID must be a positive 32-bit integer.")
    api_hash = required("API_HASH")
    session_string = required("SESSION")
    try:
        session = StringSession(session_string)
        if not session.auth_key:
            raise ValueError
    except (ValueError, struct.error):
        raise ValueError("SESSION is invalid. Generate a new one with sessiongen.py.") from None
    users = required("AUTHS").split()
    if any(not re.fullmatch(r"[1-9][0-9]{0,18}", user) or int(user) >= 2**63 for user in users):
        raise ValueError("AUTHS must contain positive Telegram user IDs separated by whitespace.")
    return int(api_id), api_hash, session, {int(user) for user in users}


def parse_link(text):
    """Ignore unrelated text and reject malformed or unsupported Telegram links."""
    text = (text or "").strip()
    if not text.lower().startswith(("https://t.me/", "http://t.me/")):
        return None
    url = urlsplit(text)
    match = POST_PATH.fullmatch(url.path)
    params = parse_qsl(url.query, keep_blank_values=True)
    if (not match or any(c.isspace() for c in text)
            or any(key not in {"single", "thread", "t"} for key, _ in params)):
        raise ValueError("Invalid or unsupported message link.")
    if match["username"] in {"c", "s"} or int(match["post"]) >= 2**31:
        raise ValueError("Invalid message link.")
    if match["topic"] and int(match["topic"]) >= 2**31:
        raise ValueError("Invalid topic ID.")
    if match["channel"]:
        channel_id = int(match["channel"])
        if channel_id >= 2**63:
            raise ValueError("Invalid channel ID.")
        return types.PeerChannel(channel_id), int(match["post"])
    return match["username"], int(match["post"])


async def copy_message(event, message):
    # raw_text and entities preserve literal Markdown and caption formatting.
    has_preview = isinstance(message.media, types.MessageMediaWebPage)

    async def send(file=None):
        video = message.video if file else None
        attributes = None
        if video:
            # Telegram uses these dimensions to lay out the inline preview.
            attributes = [
                attribute for attribute in video.attributes
                if isinstance(attribute, types.DocumentAttributeVideo)
            ]
        await event.client.send_message(
            event.chat_id, message.raw_text or "", file=file, attributes=attributes,
            formatting_entities=message.entities or [], parse_mode=None, link_preview=has_preview,
        )

    if not message.media or has_preview:
        if message.raw_text:
            await send()
        else:
            await event.reply("Message has no text or media.")
        return

    progress = await event.reply("Please wait, downloading media...")
    try:
        with TemporaryDirectory() as directory:
            file = await message.download_media(file=directory)
            if file or message.raw_text:
                await send(file)
            else:
                await event.reply("This media type cannot be copied.")
    finally:
        try:
            await progress.delete()
        except (errors.RPCError, OSError):
            log.warning("Could not clear the download status.", exc_info=True)


async def on_new_link(event):
    try:
        link = parse_link(event.raw_text)
    except ValueError as exc:
        return await event.reply(str(exc))
    if link is None:
        return
    peer, post = link
    try:
        source = await event.client.get_input_entity(peer)
        if not isinstance(source, types.InputPeerChannel):
            return await event.reply("Use a channel or supergroup message link.")
        message = await event.client.get_messages(source, ids=post)
        if not message:
            return await event.reply("Message not found.")
        await copy_message(event, message)
    except (ValueError, errors.RPCError, OSError):
        log.warning("Message request failed.", exc_info=True)
        await event.reply("Could not retrieve or send this message. Check the link and account access.")


def is_private_request(event):
    # An outgoing DM is a command only in the account's own Saved Messages.
    return event.is_private and (not event.out or event.chat_id == event.sender_id)


async def run(api_id, api_hash, session, users):
    client = TelegramClient(session, api_id, api_hash)
    client.add_event_handler(on_new_link, events.NewMessage(from_users=users, func=is_private_request))
    try:
        await client.connect()
        account = await client.get_me()
        if account is None:
            raise SystemExit("SESSION is no longer authorized. Generate a new one with sessiongen.py.")
        log.info(
            "\nClient has started as %d.\n\nJoin @BotzHub [ https://t.me/BotzHub ] for more cool bots :)",
            account.id,
        )
        await client.run_until_disconnected()
    finally:
        await client.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s")
    try:
        settings = load_settings()
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
    asyncio.run(run(*settings))
