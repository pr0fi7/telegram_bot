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