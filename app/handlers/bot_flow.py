from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.tools import call_openai_api, SYSTEM_PROMPT, build_chat_conversation, update_chat_conversation, logger, escape_markdown_v2, HR_PROMPT
from .cv_flow import CVFlow
from app.models import cvs_db
router = Router()

class ChatFlow(StatesGroup):
    waiting_for_question = State()


@router.callback_query(lambda c: c.data == "chat_with_bot")
async def chat_with_bot_handler(query: types.CallbackQuery, state: FSMContext):
    # Present follow-up: ask if the user has a CV.
    yes_btn = InlineKeyboardButton(text='Так', callback_data='have_cv_yes')
    no_btn = InlineKeyboardButton(text='Ні', callback_data='have_cv_no')
    question_btn = InlineKeyboardButton(text='Є запитання', callback_data='question_btn')
    inline_kb = InlineKeyboardBuilder([[yes_btn, no_btn], [question_btn]])
    await query.message.answer("У вас є резюме файл?", reply_markup=inline_kb.as_markup())
    await query.answer()


@router.callback_query(lambda c: c.data == "improve_cv")
async def improve_cv_handler(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cv_text = data.get("cv_text")
    # Build the prompt using the stored cv_text
    formatted_prompt = SYSTEM_PROMPT.format(text=cv_text)
    logger.info(f"Formatted prompt: {formatted_prompt}")
    
    # Build conversation (this could be a list of messages)
    conversation = await build_chat_conversation(formatted_prompt)
    ai_answer = await call_openai_api(conversation)  # Await the async call
    
    # Append the AI answer to the conversation list (if needed)
    # For example, if conversation is a list:
    conversation.append({"role": "assistant", "text": ai_answer})
    
    await query.message.answer(escape_markdown_v2(ai_answer), parse_mode="MarkdownV2")
    
    # Update the state with the new conversation
    await state.update_data({"conversation": conversation})
    await state.set_state(CVFlow.improving_cv)
    await query.answer()

@router.message(lambda message: message.text, StateFilter(CVFlow.improving_cv))
async def handle_cv_improvement(message: types.Message, state: FSMContext):
    person = message.from_user.full_name
    person_id = message.from_user.id    

    data = await state.get_data()
    conversation = data.get("conversation", [])
    
    # Append user answer
    conversation.append({"role": "user", "text": message.text})
    
    updated_conversation = await update_chat_conversation(conversation, user_query=message.text)
    ai_answer = await call_openai_api(updated_conversation)  # Await the API call
    
    await message.answer(escape_markdown_v2(ai_answer), parse_mode="MarkdownV2")
    
    # Append AI answer
    conversation.append({"role": "assistant", "text": ai_answer})
    
    # Update state with the modified conversation list
    await state.update_data({"conversation": conversation})
    
    insertion_id = data.get("insertion_id")
    if not insertion_id:
        insertion_id = cvs_db.insert_chat_conversation(person=person, person_id=person_id, conversation=conversation)
        await state.update_data({"insertion_id": insertion_id})
    else:
        await cvs_db.update_chat_conversation(insertion_id, conversation)
    
    await state.set_state(CVFlow.improving_cv)


@router.callback_query(lambda c: c.data == "question_btn")
async def question_btn_handler(query: types.CallbackQuery, state: FSMContext):  
    await query.message.answer("Які у вас є запитання?")
    await state.set_state(ChatFlow.waiting_for_question)
    await query.answer()

@router.message(StateFilter(ChatFlow.waiting_for_question))
async def handle_question(message: types.Message, state: FSMContext):
    person = message.from_user.full_name
    person_id = message.from_user.id

    conversation = await build_chat_conversation(HR_PROMPT, message.text)
    ai_answer = await call_openai_api(conversation)
    await message.answer(escape_markdown_v2(ai_answer), parse_mode="MarkdownV2")
    
    data = await state.get_data()
    hr_conversation = data.get("hr_conversation", [])
    hr_conversation.append({"role": "user", "text": message.text})
    hr_conversation.append({"role": "assistant", "text": ai_answer})
    await state.update_data({"hr_conversation": hr_conversation})
    
    insertion_id = data.get("insertion_id")
    if not insertion_id:
        insertion_id = cvs_db.insert_chat_conversation(person=person, person_id=person_id, conversation=hr_conversation)
        await state.update_data({"insertion_id": insertion_id})
    else:
        await cvs_db.update_chat_conversation(insertion_id, hr_conversation)
        
    await state.set_state(ChatFlow.waiting_for_question)
