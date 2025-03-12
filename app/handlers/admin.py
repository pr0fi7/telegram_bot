import os
from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import StatesGroup, State
from app.tools import create_conversation_file
from app.models import cvs_db  # Assumes cvs_db has methods for questions

router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Define state groups for admin authentication and operations.
class AdminAuth(StatesGroup):
    waiting_for_password = State()

class AdminState(StatesGroup):
    add_question = State()
    update_question = State()
    update_question_text = State()
    delete_question = State()
    fetch_chat_data = State()
    fetch_people_data = State()


@router.message(Command("admin"))
async def admin_auth_handler(message: types.Message, state: FSMContext):
    await message.answer("Введіть пароль :")
    await state.set_state(AdminAuth.waiting_for_password)

@router.message(StateFilter(AdminAuth.waiting_for_password))
async def check_admin_password(message: types.Message, state: FSMContext):
    if message.text != ADMIN_PASSWORD:
        await message.answer("Unauthorized access.")
        await state.clear()
        return

    await state.clear()
    # Build the admin panel menu with inline buttons.
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(
        types.InlineKeyboardButton(text="Наявні запитання", callback_data="list_questions"),
        types.InlineKeyboardButton(text="Додати запитання", callback_data="add_question")
    )
    kb_builder.row(
        types.InlineKeyboardButton(text="Оновити запитання", callback_data="update_question"),
        types.InlineKeyboardButton(text="Видалити запитання", callback_data="delete_question")
    )
    kb_builder.row(
        types.InlineKeyboardButton(text="Дані Чатів", callback_data="chat_data")
    )
    kb_builder.row(
        types.InlineKeyboardButton(text="Дані Користувачів", callback_data="people_data")
    )
    await message.answer("Вітаємо в панелі адміна, що ви хочете зробити", reply_markup=kb_builder.as_markup())

@router.callback_query(lambda c: c.data == "list_questions")
async def list_questions_handler(query: types.CallbackQuery):
    questions = cvs_db.get_predefined_questions()  # Retrieve the questions from DB
    if not questions:
        text = "No questions found."
    else:
        text = "\n".join(f"{idx+1}. {q}" for idx, q in enumerate(questions))
    await query.message.answer(f"Існуючі запитання:\n{text}")
    await query.answer()

@router.callback_query(lambda c: c.data == "add_question")
async def add_question_handler(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Будь ласка напишіть ваше запитання у такому форматі: <order>|<question_text>")
    await state.set_state(AdminState.add_question)
    await query.answer()

@router.message(StateFilter(AdminState.add_question))
async def process_add_question(message: types.Message, state: FSMContext):
    try:
        order_str, question_text = message.text.split("|", 1)
        order = int(order_str.strip())
        # Insert the new question into the database (ensure you implement this method)
        cvs_db.insert_predefined_question(question_text.strip(), order)
        await message.answer("Успішно додали нове запитання .")
    except Exception as e:
        await message.answer(f"Error adding question: {e}")
    await state.clear()

@router.callback_query(lambda c: c.data == "update_question")
async def update_question_handler(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Будь ласка введіть номер запитання для оновлення:")
    await state.set_state(AdminState.update_question)
    await query.answer()

@router.message(StateFilter(AdminState.update_question))
async def process_update_question(message: types.Message, state: FSMContext):
    try:
        order = int(message.text.strip())
        question = cvs_db.get_predefined_question(order)
        if not question:
            await message.answer(f"Question with order {order} not found.")
            await state.clear()
            return
        await state.update_data(order=order)
        await message.answer(f"Наявне запитання {order}: {question}. Введіть новий текст запитання:")
        await state.set_state(AdminState.update_question_text)
    except Exception as e:
        await message.answer(f"Error updating question: {e}")
        await state.clear()

@router.message(StateFilter(AdminState.update_question_text))
async def process_update_question_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order = data.get("order")
    question_text = message.text
    cvs_db.update_predefined_question(question_text, order)
    await message.answer("Question updated successfully.")
    await state.clear()

@router.callback_query(lambda c: c.data == "delete_question")
async def delete_question_handler(query: types.CallbackQuery, state: FSMContext):
    await query.message.answer("Будь ласка введіть номер запитання для видалення:")
    await state.set_state(AdminState.delete_question)
    await query.answer()

@router.message(StateFilter(AdminState.delete_question))
async def process_delete_question(message: types.Message, state: FSMContext):
    try:
        order = int(message.text.strip())
        question = cvs_db.get_predefined_question(order)
        if not question:
            await message.answer(f"Question with order {order} not found.")
            await state.clear()
            return
        cvs_db.delete_predefined_question(order)
        await message.answer("Question deleted successfully.")
    except Exception as e:
        await message.answer(f"Error deleting question: {e}")
    await state.clear()


@router.callback_query(lambda c: c.data == "chat_data")
async def fetch_chat_data_handler(query: types.CallbackQuery):
    admin_id = query.from_user.id
    try:
        data_list = cvs_db.get_all_chat_conversations()
        if not data_list:
            await query.message.answer("Немає даних чатів.")
        else:
            for conversation in data_list:
                # Pass the bot instance and ADMIN_ID to create_conversation_file,
                # which should convert the conversation to a file and send it to ADMIN_ID.
                await create_conversation_file(query.bot, conversation, admin_id)
        await query.answer("Дані чатів надіслані.")
    except Exception as e:
        await query.message.answer(f"Error fetching chat data: {e}")
        await query.answer()

@router.callback_query(lambda c: c.data == "people_data")
async def fetch_people_data_handler(query: types.CallbackQuery):
    admin_id = query.from_user.id
    try:
        data_list = cvs_db.get_all()
        if not data_list:
            await query.message.answer("Немає даних користувачів.")
        else:
            for entry in data_list:
                # You can create a file or simply format the text.
                # Here we assume create_conversation_file works for user data too.
                await create_conversation_file(query.bot, entry, admin_id)
        await query.answer("Дані користувачів надіслані.")
    except Exception as e:
        await query.message.answer(f"Error fetching people data: {e}")
        await query.answer()