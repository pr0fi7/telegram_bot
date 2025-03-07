import openai
from dotenv import load_dotenv
import os
import logging
from celery import shared_task
import asyncio
from app.tools import async_to_sync

load_dotenv()
logging.basicConfig(level=logging.INFO)
client = openai.AsyncClient(api_key=os.getenv("OPENAI_API"))


async def fetch_answer(question: str) -> str:
    response = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

# @shared_task
async def get_answer(question: str) -> str:
    # loop = asyncio.new_event_loop()
    # try:
    #     answer = loop.run_until_complete(fetch_answer(question))
    # finally:
    #     loop.close()

    answer = await fetch_answer(question)
    return answer