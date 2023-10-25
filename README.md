# Telegram Bot
https://mastergroosha.github.io/telegram-tutorial-2/quickstart/

docker run -d -p 8081:8081 --name=telegram-bot-api --restart=always -v telegram-bot-api-data:/var/lib/telegram-bot-api -e TELEGRAM_API_ID=17461895 -e TELEGRAM_API_HASH=2bfaea00c1edb7e3bd8cb624ed58e113 aiogram/telegram-bot-api:latest

https://api.telegram.org/bot5605913205:AAEi20ubh7RK2PRA5F01XEjfP2Sr7mk2cAI/logOut
{'ok': True, 'result': True}
{"ok":false, "error_code":400, "description":"Logged out"}