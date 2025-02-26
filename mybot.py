import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web

logging.basicConfig(level=logging.INFO)

# Load token from environment variables
TOKEN = os.getenv("TELEGRAM_API")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Define your message handler (aiogram v2 style; adjust if using v3)
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

# Create an aiohttp web application configured for webhooks
app = setup_application(dispatcher=dp, path="/webhook")

# This function is what Cloud Functions will call for HTTP requests.
async def telegram_webhook(request: web.Request):
    # Process the incoming update from Telegram
    data = await request.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return web.Response(text="OK")

# Add the webhook endpoint to the app
app.router.add_post("/webhook", telegram_webhook)

# If running locally, you can start aiohttp server:
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
