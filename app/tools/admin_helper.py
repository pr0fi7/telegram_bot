from dotenv import load_dotenv
import os
from app.models import cvs_db
from io import BytesIO
import json 
from datetime import datetime

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID"))


async def notify_admin_new_entry(bot, id):
    admin_id = ADMIN_ID
    json_entry = cvs_db.get_by_id(id)
    person_name = json_entry.get("person")
    raw_text = json_entry.get("raw_text")
    formatted_text = json_entry.get("formatted_text")
    entry_summary = f"New entry from {person_name}:\n{raw_text}\n\nSummary:\n{formatted_text}"
    await bot.send_message(admin_id, entry_summary)


import tempfile
from aiogram.types import FSInputFile

async def create_conversation_file(bot, conversation_json, admin_id):
    # Convert the conversation JSON to a formatted string.
    conversation_str = json.dumps(
        conversation_json, 
        indent=4, 
        ensure_ascii=False, 
        default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o)
    )
    
    # Write the conversation string to a temporary file.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp.write(conversation_str.encode("utf-8"))
        tmp.flush()
        file_path = tmp.name

    # Create an FSInputFile from the temporary file.
    input_file = FSInputFile(file_path)
    
    await bot.send_document(admin_id, input_file)
