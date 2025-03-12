
from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.tools import call_openai_api, SYSTEM_PROMPT, build_chat_conversation, update_chat_conversation, logger, escape_markdown_v2
from .cv_flow import CVFlow

router = Router()


@router.callback_query(lambda c: c.data == "chat_with_bot")
async def chat_with_bot_handler(query: types.CallbackQuery, state: FSMContext):
    # Present follow-up: ask if the user has a CV.
    yes_btn = InlineKeyboardButton(text='Так', callback_data='have_cv_yes')
    no_btn = InlineKeyboardButton(text='Ні', callback_data='have_cv_no')
    inline_kb = InlineKeyboardBuilder([[yes_btn, no_btn]])
    await query.message.answer("У вас є резюме файл?", reply_markup=inline_kb.as_markup())
    await query.answer()

@router.callback_query(lambda c: c.data == "improve_cv")
async def improve_cv_handler(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cv_text = data.get("cv_text")

    formatted_prompt = SYSTEM_PROMPT.format(text=cv_text)
    logger.info(f"Formatted prompt: {formatted_prompt}")
    conversation = await build_chat_conversation(formatted_prompt)
    ai_answer = await call_openai_api(conversation)  # Await the async call
    await query.message.answer(escape_markdown_v2(ai_answer), parse_mode="MarkdownV2")
    updated_conversation = await update_chat_conversation(conversation, ai_answer=ai_answer)
    await state.update_data({"conversation": updated_conversation})
    await state.set_state(CVFlow.improving_cv)
    await query.answer()

@router.message(lambda message: message.text, StateFilter(CVFlow.improving_cv))
async def handle_cv_improvement(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conversation = data.get("conversation")
    updated_conversation = await update_chat_conversation(conversation, user_query=message.text)
    ai_answer = await call_openai_api(updated_conversation)  # Await this call too
    await message.answer(escape_markdown_v2(ai_answer), parse_mode="MarkdownV2")
    new_updated_conversation = await update_chat_conversation(updated_conversation, ai_answer=ai_answer)
    await state.update_data({"conversation": new_updated_conversation})
    await state.set_state(CVFlow.improving_cv)
