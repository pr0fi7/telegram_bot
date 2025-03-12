from aiogram import Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.models import cvs_db
from app.tools import call_openai_api, json_schema, build_conversation, SUMMARY_PROMPT, notify_admin_new_entry
router = Router()

class ConversationFlow(StatesGroup):
    waiting_for_info = State()

@router.callback_query(lambda c: c.data == "have_cv_no")
async def have_cv_no_handler(query: types.CallbackQuery, state: FSMContext):
    questions = cvs_db.get_predefined_questions()
    if not questions:
        await query.message.answer("No questions found. Please contact the admin.")
        return
    
    # Initialize conversation data: store an empty list and start index 0
    await state.update_data(conversation=[], question_index=0, questions=questions)
    first_question = questions[0]
    await query.message.answer(f"Розпочнемо: {first_question}")
    await state.set_state(ConversationFlow.waiting_for_info)
    await query.answer()

@router.message(StateFilter(ConversationFlow.waiting_for_info))
async def conversation_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conversation = data.get("conversation", [])
    question_index = data.get("question_index", 0)
    questions = data.get("questions", [])

    # Record the answer for the current question
    current_question = questions[question_index]
    conversation.append({current_question: message.text})
    question_index += 1

    if question_index < len(questions):
        # Update state and ask next question
        next_question = questions[question_index]
        await state.update_data(conversation=conversation, question_index=question_index)
        await message.answer(f"Question {question_index+1}: {next_question}")
    else:
        # All questions have been answered
        summary_lines = []
        for idx, qa in enumerate(conversation, start=1):
            for question, answer in qa.items():
                summary_lines.append(f"Q{idx}: {question}\nA{idx}: {answer}")
        summary = "\n\n".join(summary_lines)
        await message.answer(f"Дякую за відповіді!")
        current_id = cvs_db.insert(message.from_user.full_name, raw_text=summary)
        conversation = await build_conversation(SUMMARY_PROMPT, summary)
        summary = call_openai_api(conversation, json_schema)
        update = cvs_db.update(current_id, formatted_text=summary)
        await notify_admin_new_entry(current_id)
        await message.answer(f"Ваше резюме:\n{summary}")

@router.message(lambda message: message.text and message.text.lower() == "done", StateFilter(ConversationFlow.waiting_for_info))
async def finish_conversation_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conversation = data.get("conversation", [])
    summary_lines = []
    for idx, qa in enumerate(conversation, start=1):
        for question, answer in qa.items():
            summary_lines.append(f"Q{idx}: {question}\nA{idx}: {answer}")
    summary = "\n\n".join(summary_lines)
    await message.answer(f"Підсумок:\n{summary}")
    await state.clear()
