import asyncio
import os
import re
import random
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.session.aiohttp import AiohttpSession

import google.generativeai as genai
import swisseph as swe

from dotenv import load_dotenv

# ==========================================
# LOAD ENV
# ==========================================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing in .env")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY missing in .env")

# ==========================================
# GEMINI CONFIG
# ==========================================
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash"
)

# ==========================================
# TELEGRAM CONFIG
# ==========================================
session = AiohttpSession()

bot = Bot(
    token=BOT_TOKEN,
    session=session
)

dp = Dispatcher()

# ==========================================
# DATABASE
# ==========================================
def init_db():

    conn = sqlite3.connect("jyotish_memory.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            name TEXT,
            dob TEXT,
            tob TEXT,
            city TEXT,
            sun_deg REAL,
            moon_deg REAL
        )
    """)

    conn.commit()
    conn.close()

def save_user(chat_id, name, dob, tob, city, sun, moon):

    conn = sqlite3.connect("jyotish_memory.db")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users
        (chat_id, name, dob, tob, city, sun_deg, moon_deg)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (chat_id, name, dob, tob, city, sun, moon))

    conn.commit()
    conn.close()

def get_user(chat_id):

    conn = sqlite3.connect("jyotish_memory.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE chat_id = ?",
        (chat_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return user

# ==========================================
# KUNDALI ENGINE
# ==========================================
def calculate_planets(dob, tob):

    try:

        d, m, y = map(int, dob.split("-"))

        nums = re.findall(r"\d+", tob)

        h = int(nums[0])
        mn = int(nums[1]) if len(nums) > 1 else 0

        if "PM" in tob.upper() and h < 12:
            h += 12

        swe.set_ephe_path()

        jd = swe.julday(y, m, d, h + mn / 60)

        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]

        return sun, moon

    except Exception:
        return 0.0, 0.0

# ==========================================
# STATES
# ==========================================
class Profile(StatesGroup):

    name = State()
    dob = State()
    tob = State()
    city = State()
    palm = State()

# ==========================================
# START FLOW
# ==========================================
@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):

    await state.clear()

    user = get_user(message.chat.id)

    if user:

        return await message.answer(
            f"🙏 Welcome back {user[1]}.\n\nWhat guidance do you seek today?"
        )

    await message.answer(
        """
🙏 Namaste.

I am Jyotish Guruji.

People often come to me when life feels uncertain...
whether it is business, relationships, career, or timing.

Let us begin calmly.

What is your full name?
"""
    )

    await state.set_state(Profile.name)

# ==========================================
# PROFILE FLOW
# ==========================================
@dp.message(Profile.name)
async def process_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)

    await message.answer(
        f"Swagat {message.text}.\n\nYour birth date? (DD-MM-YYYY)"
    )

    await state.set_state(Profile.dob)

@dp.message(Profile.dob)
async def process_dob(message: Message, state: FSMContext):

    await state.update_data(dob=message.text)

    await message.answer(
        "Your birth time? (Example: 10:45 PM)"
    )

    await state.set_state(Profile.tob)

@dp.message(Profile.tob)
async def process_tob(message: Message, state: FSMContext):

    await state.update_data(tob=message.text)

    await message.answer(
        "Your birth city?"
    )

    await state.set_state(Profile.city)

@dp.message(Profile.city)
async def process_city(message: Message, state: FSMContext):

    await state.update_data(city=message.text)

    await message.answer(
        "Now upload a photo of your RIGHT palm for spiritual analysis."
    )

    await state.set_state(Profile.palm)

# ==========================================
# PALM FLOW
# ==========================================
@dp.message(Profile.palm, F.photo)
async def process_palm(message: Message, state: FSMContext):

    await bot.send_chat_action(
        message.chat.id,
        ChatAction.TYPING
    )

    data = await state.get_data()

    sun, moon = calculate_planets(
        data["dob"],
        data["tob"]
    )

    save_user(
        message.chat.id,
        data["name"],
        data["dob"],
        data["tob"],
        data["city"],
        sun,
        moon
    )

    await asyncio.sleep(2)

    await message.answer(
        f"""
✨ Scan Complete ✨

I can already sense strong emotional depth in your energy.

☀️ Sun Degree: {sun:.1f}°
🌙 Moon Degree: {moon:.1f}°

Your spiritual profile has been prepared.

Now tell me...
what is troubling your heart today?
"""
    )

    await state.clear()

# ==========================================
# MAIN CHAT
# ==========================================
@dp.message()
async def guru_chat(message: Message):

    await bot.send_chat_action(
        message.chat.id,
        ChatAction.TYPING
    )

    user = get_user(message.chat.id)

    name = user[1] if user else "Seeker"

    system_prompt = f"""
You are Jyotish Guruji.

You are:
- emotionally wise
- spiritual
- calm
- observant
- human-like

Never sound robotic.

Speak like a real Indian astro guru.

User name: {name}

Keep responses conversational and emotionally immersive.
"""

    final_prompt = f"""
{system_prompt}

User message:
{message.text}
"""

    try:

        await asyncio.sleep(
            random.uniform(1.5, 3)
        )

        response = model.generate_content(
            final_prompt
        )

        reply = response.text.strip()

        if not reply:
            reply = "🙏 The energies feel unclear right now. Ask me once more calmly."

        await message.answer(reply)

    except Exception as e:

        print("AI ERROR:", e)

        await message.answer(
            "🙏 Cosmic energies feel unstable right now. Please ask again shortly."
        )

# ==========================================
# MAIN
# ==========================================
async def main():

    init_db()

    print("🕉️ Jyotish Guruji Stable Build Running...")

    await dp.start_polling(
        bot,
        request_timeout=60
    )

if __name__ == "__main__":
    asyncio.run(main())
