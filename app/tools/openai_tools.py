import base64
import aiohttp
import openai
from .config import OPENAI_API
import numpy as np
from PIL import Image
# from gemini import gemini_upload_and_chat
from openai import AsyncOpenAI
from io import BytesIO
import cv2
import json
# from pydantic import BaseModel
# from celery import shared_task
from .mylogger import logger

# json_schema = {
#   "type": "json_schema",
#   "json_schema": {
#     "name": "OpenAIOutput",
#     "schema": {
#       "title": "OpenAIOutput",
#       "type": "object",
#       "properties": {
#         "project_name": {
#           "type": "string",
#           "description": "The name of the project."
#         },
#         "project_subname": {
#           "type": "string",
#           "description": "The subname or subtitle of the project."
#         },
#         "introduction": {
#           "type": "string",
#           "description": "An introduction describing the project."
#         },
#         "objective": {
#           "type": "string",
#           "description": "The project's objective."
#         },
#         "approach": {
#           "type": "string",
#           "description": "The approach used to achieve the project's goals."
#         },
#         "budget_text": {
#           "type": "string",
#           "description": "Text describing the budget for the project."
#         },
#         "budget_estimates": {
#           "type": "array",
#           "items": {
#             "type": "object",
#             "properties": {
#               "service_type": {"type": "string"},
#               "steps": {
#                 "type": "array",
#                 "items": {
#                   "type": "object",
#                   "properties": {
#                     "step": {"type": "string"},
#                     "cost": {"type": "number"},
#                     "duration": {"type": "integer"}
#                   },
#                   "required": ["step", "cost", "duration"]
#                 }
#               }
#             },
#             "required": ["service_type", "steps"]
#           }
#         }
#       },
#       "required": [
#         "project_name",
#         "project_subname",
#         "introduction",
#         "objective",
#         "approach",
#         "budget_text",
#         "budget_estimates"
#       ]
#     }
#   }
# }

async def call_openai_api(conversation: list[dict], model: str = "gpt-4o-mini") -> dict:
    """
    Asynchronously call the OpenAI API and return the parsed JSON response.
    """
    client = openai.Client()
    client.api_key = OPENAI_API  # make sure OPENAI_API is defined correctly

    try:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=conversation,
            temperature=0.7,
            max_tokens=15000
        )
        logger.info("Full response: %s", response)
        
        content = response.choices[0].message.content.strip()
        logger.info("Content: %s", content)
        
        if not content:
            raise ValueError("OpenAI API returned an empty response")

        return content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise e

def load_image(image_bytes):
    # Ensure the image file is opened correctly
    print("Type of image_bytes:", type(image_bytes))

    image = Image.open(BytesIO(image_bytes))
    image = image.convert('RGB')  # Ensure image is in RGB format
    image_array = np.array(image)
    return image_array

async def fetch_image_text(session, api_key, base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is on the image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
        result = await response.json()
        return result['choices'][0]['message']['content']


async def getWhatOnImage(image_bytes):
    # OpenAI API Key
    api_key = OPENAI_API

    image = load_image(image_bytes)
    _, buffer = cv2.imencode('.jpg', image)
    base64_image = base64.b64encode(buffer.tobytes()).decode('utf-8')

    # async with aiohttp.ClientSession() as session:
    #     tasks = fetch_image_text(session, api_key, base64_image)
    #     results = await asyncio.gather(*tasks)
    async with aiohttp.ClientSession() as session:
        results = await fetch_image_text(session, api_key, base64_image)
    return results



async def get_openai_embeddings(
    texts: list[str],
    model: str = "text-embedding-3-small",
    base_url: str = None,
    api_key: str = None,
) -> np.ndarray:
    openai.api_key = api_key or OPENAI_API
    openai_async_client = (
        AsyncOpenAI() if base_url is None else AsyncOpenAI(base_url=base_url)
    )
    response = await openai_async_client.embeddings.create(
        model=model, input=texts, encoding_format="float"
    )
  
    return np.array([dp.embedding for dp in response.data])
