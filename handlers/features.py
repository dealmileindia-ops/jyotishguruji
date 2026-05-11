from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.kundali import generate_kundali
from services.muhurat import get_muhurat
from vision.palm import palm_reading

router = Router()

@router.message(Command("kundali"))
async def kundali(message: Message):
    result = generate_kundali()

    await message.answer(
        f"🔭 Kundali Reading\n\n"
        f"Moon Sign: {result['moon']}\n"
        f"Nakshatra: {result['nakshatra']}\n"
        f"Dasha: {result['dasha']}"
    )

@router.message(Command("muhurat"))
async def muhurat(message: Message):
    result = get_muhurat()

    await message.answer(
        f"🕉 शुभ मुहूर्त\n\n"
        f"Best Time: {result['time']}\n"
        f"{result['note']}"
    )

@router.message(Command("palm"))
async def palm(message: Message):
    result = await palm_reading()

    await message.answer(
        f"🖐 Palm Energy Reading\n\n{result}"
    )