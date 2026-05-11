from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from services.memory import set_language

router = Router()

def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
                InlineKeyboardButton(text="🇮🇳 हिन्दी", callback_data="lang_hi")
            ],
            [
                InlineKeyboardButton(text="🇮🇳 मराठी", callback_data="lang_mr"),
                InlineKeyboardButton(text="🇮🇳 தமிழ்", callback_data="lang_ta")
            ]
        ]
    )

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🙏 Welcome Seeker...\n\nChoose your language.",
        reply_markup=language_keyboard()
    )