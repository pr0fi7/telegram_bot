from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter, CommandStart

router = Router()

class ChatState(StatesGroup):
    giving_consent = State()
    waiting_for_question = State()

@router.message(CommandStart())
async def ask_question(message: types.Message, state: FSMContext):
    """ Asks for personal data consent """
    await state.set_state(ChatState.giving_consent)

    yes_btn = InlineKeyboardButton(text='Так', callback_data='yes_btn')
    no_btn = InlineKeyboardButton(text='Ні', callback_data='no_btn')

    # Correctly build the inline keyboard
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[[yes_btn, no_btn]])

    await message.answer("Ви згодні на обробку персональних даних?", reply_markup=inline_kb)

@router.callback_query(lambda c: c.data == "yes_btn")
async def ask_state_question(query: types.CallbackQuery, state: FSMContext):
    """ Asks what type of chat the user wants after consent """
    await state.set_state(ChatState.waiting_for_question)
    await query.answer()  # Acknowledge callback to avoid Telegram warning

    create_bot_btn = InlineKeyboardButton(text='Чат з Ботом🤖', callback_data='chat_with_bot')
    go_person_btn = InlineKeyboardButton(text='Чат з Людиною', callback_data='chat_with_person')

    # Correctly build the inline keyboard
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[[create_bot_btn, go_person_btn]])

    await query.message.answer("Вітаю! Як я можу вам допомогти?", reply_markup=inline_kb)
