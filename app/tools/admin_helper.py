from dotenv import load_dotenv
import os
from models import cvs_db
import csv
import tempfile
from datetime import datetime
from aiogram.types import FSInputFile

load_dotenv()


async def notify_admin_new_entry(bot, id):
    """ Sends a notification to the admin about a new entry """
    json_entry = cvs_db.get_by_id(id)
    person_name = json_entry.get("person")
    raw_text = json_entry.get("raw_text")
    formatted_text = json_entry.get("formatted_text")
    entry_summary = f"New entry from {person_name}:\n{raw_text}\n\nSummary:\n{formatted_text}"
    await bot.send_message(id, entry_summary)
import csv
import json
import tempfile
from datetime import datetime
from aiogram.types import FSInputFile

def flatten_dict(data: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    Recursively flattens a nested dictionary.
    Example:
        {
          "person": {"name": "Mark", "age": 25},
          "metadata": {"tags": ["Python", "Aiogram"]},
          "title": "Developer"
        }
    becomes:
        {
          "person.name": "Mark",
          "person.age": 25,
          "metadata.tags": '["Python", "Aiogram"]',
          "title": "Developer"
        }
    """
    items = {}
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            items.update(flatten_dict(value, new_key, sep=sep))
        elif isinstance(value, list):
            # Store lists as JSON strings (you could flatten them further if desired)
            items[new_key] = json.dumps(value, ensure_ascii=False)
        else:
            items[new_key] = value
    return items

async def create_flexible_csv(bot, data, admin_id: int, filename="data.csv"):
    """
    Creates a CSV from any list/dict data, flattening nested dictionaries.
    Sends the CSV to the specified admin_id via Aiogram.

    :param bot: Aiogram Bot instance
    :param data: A list of dicts or a single dict
    :param admin_id: Telegram user ID to send the file to
    :param filename: The name of the file (default: 'data.csv')
    """
    # If data is a single dict, wrap it in a list for uniform processing
    if isinstance(data, dict):
        data = [data]

    # Flatten each dictionary in the list
    flattened_data = []
    for item in data:
        if isinstance(item, dict):
            flattened_data.append(flatten_dict(item))
        else:
            # If it's not a dict, store it as a simple row with a "value" column
            flattened_data.append({"value": str(item)})

    # Collect all unique keys across all flattened dicts
    all_keys = set()
    for item in flattened_data:
        all_keys.update(item.keys())
    # Sort keys for consistent column ordering
    fieldnames = sorted(all_keys)

    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv",
        mode="w",
        newline="",
        encoding="utf-8-sig"
    ) as tmp_file:
        writer = csv.DictWriter(tmp_file, fieldnames=fieldnames)
        writer.writeheader()
        for item in flattened_data:
            writer.writerow(item)

        tmp_file.flush()
        file_path = tmp_file.name

    # Send the file as a document
    input_file = FSInputFile(file_path, filename=filename)
    await bot.send_document(admin_id, input_file)
