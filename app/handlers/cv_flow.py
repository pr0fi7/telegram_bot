from aiogram import Router, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from tools import logger, call_openai_api, SUMMARY_PROMPT, json_schema, build_conversation, notify_admin_new_entry
from models import cvs_db
from handle_file import extract_text_from_file, add_to_qdrant
from dotenv import load_dotenv
import os

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))
router = Router()

class CVFlow(StatesGroup):
    waiting_for_cv_upload = State()
    improving_cv = State()

@router.callback_query(lambda c: c.data == "have_cv_yes")
async def have_cv_yes_handler(query: types.CallbackQuery, state: FSMContext):
    # Start the CV flow: ask for file upload.
    await query.message.answer("Прекрасно! Будь ласка, завантажте своє резюме.")
    await state.set_state(CVFlow.waiting_for_cv_upload)
    await query.answer()

@router.message(lambda message: message.document, StateFilter(CVFlow.waiting_for_cv_upload))
async def handle_cv_upload(message: types.Message, state: FSMContext):

    improve_cv_btn = InlineKeyboardButton(text='Покращити резюме', callback_data='improve_cv')
    finish_btn = InlineKeyboardButton(text='Завершити', callback_data='finish')
    inline_kb = InlineKeyboardBuilder([[improve_cv_btn, finish_btn]])

    file = message.document
    file_name = file.file_name
    file_io = await message.bot.download(file)
    file_bytes = file_io.getvalue()
    # Process the file (e.g., extract text and store it).
    file_text = extract_text_from_file(file_bytes)
    logger.info(f"Extracted text from CV: {file_text}")

    person_name = message.from_user.full_name  
    person_id = message.from_user.id
    new_id = cvs_db.insert(person_name, raw_text=file_text)
    await state.update_data(cv_text=file_text, cv_id=new_id, person_id=person_id)
    logger.info(f"Inserted CV record with ID: {new_id}")

    # Add the CV to the search index
    result = add_to_qdrant(file_text, file_name, person_id)
    conversation = await build_conversation(SUMMARY_PROMPT, file_text)
    summary = await call_openai_api(conversation, json_schema)
    update = cvs_db.update(new_id,person_name=person_name, formatted_text=summary)
    logger.info(f"Updated CV record with ID: {new_id}")
    await notify_admin_new_entry(message.bot, new_id, ADMIN_ID)

    await message.answer("Ваше резюме було успішно завантажено!")
    await message.answer("Дякую за завантаження резюме! Якщо ви хочете покращити його, натисніть на кнопку нижче.", reply_markup=inline_kb.as_markup())


    # await state.clear()