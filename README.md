# GetRestrictedMessages
Telegram bot to copy messages from chats (both private and public) with forward restrictions enabled.


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

- `API_ID` - Telegram API ID from [my.telegram.org](https://my.telegram.org)
- `API_HASH` - Telegram API HASH from [my.telegram.org](https://my.telegram.org)
- `SESSION` - Telethon session string. Get it by running `python sessiongen.py` locally.
- `AUTHS` - List of telegram user IDs who can use the bot, split by space.

A sample .env file would look like this:
```env
API_ID=123
API_HASH=abcdefd
SESSION=1Babcdefg
AUTHS=719195224 12345678
```



## Deployment
[![Video Tutorial](https://img.shields.io/youtube/views/uk6kd29C9E8?label=Deploying%20Tutorial)](https://www.youtube.com/watch?v=uk6kd29C9E8)

[![DigitalOcean Referral Badge](https://web-platforms.sfo2.digitaloceanspaces.com/WWW/Badge%203.svg)](https://www.digitalocean.com/?refcode=7b7d6a915392&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)


To deploy this bot, run:

```shell
git clone https://github.com/xditya/GetRestrictedMessages
cd GetRestrictedMessages
pip install -r requirements.txt
cp .env.sample .env
nano .env [ fill the values and exit with ctrl+s and then ctrl+x ]
python main.py
```

OR

You can use other platforms that offer free deployments.
## Support

For support, use the GitHub discussions tab, or join the support chat on telegram by clicking [here](https://t.me/BotzHubChat).


## License

[GNU AFFERO GENERAL PUBLIC LICENSE](./LICENSE)


## Authors

- [@xditya](https://xditya.me)

