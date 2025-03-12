from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()  # Clear any previous state if needed
    create_bot_btn = InlineKeyboardButton(text='Чат з Ботом🤖', callback_data='chat_with_bot')
    go_person_btn = InlineKeyboardButton(text='Чат з Людиною', callback_data='chat_with_person')

    inline_kb = InlineKeyboardBuilder([[create_bot_btn, go_person_btn]])
    await message.answer(
        "Вітаю! Як я можу вам допомогти?",
        reply_markup=inline_kb.as_markup()
    )
