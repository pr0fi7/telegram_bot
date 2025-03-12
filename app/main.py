import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from .handlers import nocv_flow, start, cv_flow, admin, person_flow, bot_flow
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Register routers/handlers from different modules
dp.include_router(start.router)
dp.include_router(cv_flow.router)
dp.include_router(nocv_flow.router)
dp.include_router(admin.router)
dp.include_router(person_flow.router)
dp.include_router(bot_flow.router)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



# import os
# import asyncio
# from app.tools import logger, call_openai_api
# import sys
# from aiogram import Bot, Dispatcher, html, types
# from aiogram.enums import ParseMode
# from aiogram.filters import CommandStart
# from aiogram.types import File
# from openai_requests import get_answer
# from handle_file import add_to_qdrant, extract_text_from_file, query
# from aiogram.client.default import DefaultBotProperties
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# import html

# # Load token from environment variables
# TOKEN = os.getenv("TELEGRAM_API")
# if not TOKEN:
#     logger.error("TELEGRAM_API token is missing. Please set it in the environment variables.")
#     sys.exit(1)

# # Initialize bot
# bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# dp = Dispatcher()

# ### 1. Command Start Handler
# @dp.message(CommandStart())
# async def command_start_handler(message: types.Message) -> None:
#     await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

# ### 2. Text Message Handler
# @dp.message()
# async def echo_handler(message: types.Message) -> None:
#     create_doc_btn = types.InlineKeyboardButton(text='Create a document', callback_data='create_document')
#     cancel_btn = types.InlineKeyboardButton(text='Back to Chat', callback_data='back_to_chat')

#     inline_kb = InlineKeyboardBuilder([[create_doc_btn, cancel_btn]])

#     if message.text:
#         try:
#             answer = await get_answer(message.text)
#             logger.info(f"AI Response: {answer}")
#             await message.answer(answer)
#         except Exception as e:
#             logger.exception("Error processing message: %s", e)
#             await message.answer("Nice try!")

#     elif message.document:
#         logger.info("Message received: %s", message)
#         await message.answer("I see you've uploaded a file. Let me take a look...")

#         file = message.document
#         file_name = file.file_name

#         # Download file into a BytesIO stream
#         file_io = await bot.download(file)
#         # Extract bytes from the BytesIO stream
#         file_bytes = file_io.getvalue()
        
#         file_text = extract_text_from_file(file_bytes)

#         logger.info("File received: %s", file_name)
#         logger.info("File text: %s", file_text)

#         # In your handler:
#         result = add_to_qdrant(file_text, file_name, "documents")

#         # Wait for the celery task to complete without blocking the event loop
#         loop = asyncio.get_running_loop()
#         await loop.run_in_executor(None, result.get)

#         # Now build conversation and call OpenAI API
#         conversation = await build_conversation(message.text, "documents")

#         await message.answer('Welcome! Click the button below:', reply_markup=inline_kb.as_markup())
#         ai_answer = await call_openai_api(conversation)

#         await message.answer(html.escape(ai_answer), parse_mode='MarkdownV2')

# async def build_conversation(user_query:str, collection_name:str = "documents") -> dict:
#     results = await query(user_query, collection_name)
#     conversation = [
#         {"role": "system", "content": f"You are a helpful assistant. Use the following information to help you. {results}"},
#         {"role": "user", "content": user_query}
#     ]
#     return conversation

# ### 4. Bot Start Function
# async def main() -> None:
#     await dp.start_polling(bot)

# ### 5. Script Execution
# if __name__ == "__main__":
#     asyncio.run(main())
