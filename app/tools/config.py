from dotenv import load_dotenv
import os


load_dotenv()

TELGRAM_API = os.getenv("TELEGRAM_API")
OPENAI_API = os.getenv("OPENAI_API_KEY")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

QDRANT_CLIENT_HOST = os.getenv("QDRANT_CLIENT_HOST")


GEMINI_PROMPT : str = """
Your tasks are:

1. Perform thorough OCR on all pages of the provided document or image.

2. Extract ALL written text, ensuring no information is missed.

3. Double-check and verify the following elements for consistency across the entire document:
   a. Names
   b. Numbers
   c. Dates
   d. People mentioned
   e. Checkboxes (checked or unchecked)
   f. Phone numbers

4. Ensure logical consistency of dates and names throughout the document.

5. Verify that all extracted information is coherent and makes sense in context.

6. Provide a comprehensive and accurate transcription of the entire document without page separation.

7. Return the transcription in a clean, readable format. If there are several languages present in the document, separate the text by language.

Remember: Accuracy, completeness, and consistency are your top priorities. Do not omit any text, no matter how insignificant it may seem.
Return only the text without explanations or comments. If there is no text, no images, or the document is blank, return an empty string.
""".strip()

SUMMARY_PROMPT: str = """
Проаналізуйте наступну інформацію та надайте підсумок.
Інформація: {text}
Ваша відповідь повинна суворо відповідати наступному формату:
1. Ім'я: name
2. Вік: age
3. Поточна посада: occupation
4. Освітні кваліфікації: education
5. Досвід роботи: experience
6. Навички: skills
7. Майбутні амбіції: aspirations

Якщо інформації немає, будь ласка, поверніть порожній рядок ("").
Завжди видавайте відповідь українською мовою.
""".strip()

SYSTEM_PROMPT = '''
Проаналізуйте наступну інформацію щодо резюме. І надай ідеї для покращення.
Інформація: {text}
'''.strip()

HR_PROMPT = '''' \
Ти експерт в сфері рекрутингу. Намагайся допомогти використовуючи всі знання з рекрутингу які ти маєш.
'''

async def build_chat_conversation(SYSTEM_PROMPT: str, user_query: str = "") -> str:
    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
    return conversation

async def update_chat_conversation(conversation: list, user_query: str = "", ai_answer: str = "") -> list:
    if ai_answer:
        conversation.append({"role": "assistant", "content": ai_answer})
    if user_query:
        conversation.append({"role": "user", "content": user_query})
    return conversation

async def build_conversation(prompt: str, summary_text: str) -> list[dict]:
    # Format the prompt so that only the {cv_text} placeholder is replaced
    formatted_prompt = prompt.format(text=summary_text)
    return [
        {"role": "system", "content": formatted_prompt},
    ]

json_schema = {
  "type": "json_schema",
  "json_schema": {
    "name": "OpenAIOutput",
    "schema": {
      "title": "OpenAIOutput",
      "type": "object",
      "properties": {
          "name": {
          "type": "string",
          "description": "The name of the person."
        },
            'age': {
            'type': 'string',  
            'description': 'The age of the person.'
        },
        'occupation': {
            'type': 'string',  
            'description': 'The current occupation of the person.'
        },
        'education': {
            'type': 'string',  
            'description': 'The educational qualifications of the person.'
        },
        'experience': {
            'type': 'string',  
            'description': 'The work experience of the person.'
        },
        'skills': {
            'type': 'string',  
            'description': 'The skills of the person.'
        },
        'aspirations': {
            'type': 'string',  
            'description': 'The future aspirations of the person.'
        }
      }
    }
    }
}


# async def build_conversation(user_query:str, collection_name:str = "documents") -> dict:
#     documents_text = query()
#     conversation = [
#         {"role": "system", "content": f"You are a helpful assistant. Use the following information to help you. {results}"},
#         {"role": "user", "content": user_query}
#     ]
#     return conversation