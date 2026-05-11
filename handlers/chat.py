from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from services.memory import set_language, get_language, save_memory
from services.ai_engine import guru_reply

router = Router()

@router.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: CallbackQuery):
    lang = callback.data.replace("lang_", "")
    set_language(callback.from_user.id, lang)

    msgs = {
        "en": "🙏 Tell me what is troubling your heart today...",
        "hi": "🙏 आज आपके मन में क्या चल रहा है?",
        "mr": "🙏 आज तुमच्या मनात काय चाललं आहे?",
        "ta": "🙏 இன்று உங்கள் மனதில் என்ன இருக்கிறது?"
    }

    await callback.message.answer(msgs.get(lang, msgs["en"]))

@router.message()
async def normal_chat(message: Message):
    save_memory(message.from_user.id, message.text)

    lang = get_language(message.from_user.id)

    response = await guru_reply(
        user_id=message.from_user.id,
        text=message.text,
        language=lang
    )

    await message.answer(response)