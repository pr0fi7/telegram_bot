import os
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(lambda c: c.data == "chat_with_person")
async def chat_with_person_handler(query: types.CallbackQuery, state: FSMContext):
    # You can add logic to connect to a human operator here.
    await query.message.answer("Як тільки ми знайдемо фахівця, який може вам допомогти, ми зв'яжемося з вами.")
    await query.answer()