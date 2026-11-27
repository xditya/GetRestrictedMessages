from telethon import TelegramClient
from telethon.sessions import StringSession

def main():
    try:
        api_id = int(input("Enter API ID: "))
        if not 0 < api_id < 2**31:
            raise ValueError
    except ValueError:
        raise SystemExit("API ID must be a positive 32-bit integer.") from None
    api_hash = input("Enter API HASH: ").strip()
    if not api_hash:
        raise SystemExit("API HASH is required.")

    with TelegramClient(StringSession(), api_id, api_hash) as client:
        print("Here is your session string:\n" + client.session.save())


if __name__ == "__main__":
    main()
