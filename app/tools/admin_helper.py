from dotenv import load_dotenv
import os
from app.models import cvs_db
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
    