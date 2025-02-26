import openai

from dotenv import load_dotenv
import os
import logging
from celery import shared_task

load_dotenv()
logging.basicConfig(level=logging.INFO)
client = openai.AsyncClient(api_key=os.getenv("OPENAI_API"))

@shared_task
async def get_answer(question: str) -> str:
    response = await client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}] 
        
    )
    logging.info(response)
    return response.choices[0].message.content
