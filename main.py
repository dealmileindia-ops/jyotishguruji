import asyncio
import random
import sqlite3
import requests
import re
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

import swisseph as swe

# =========================================================
# TOKENS
# =========================================================

BOT_TOKEN = os.getenv("8643055140:AAEDtBPoSX3Ht_0KcFE7YHUg1nktaHARKzU")

GROQ_API_KEY = os.getenv("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")

# =========================================================
# TELEGRAM
# =========================================================

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(
    "users.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    name TEXT,
    dob TEXT,
    tob TEXT,
    city TEXT,
    moon_sign TEXT,
    nakshatra TEXT,
    lagna TEXT,
    career_house TEXT,
    relationship_house TEXT,
    money_house TEXT,
    dasha TEXT,
    dasha_effect TEXT,
    personality TEXT,
    last_topic TEXT,
    last_question TEXT,
    emotional_state TEXT
)
""")

conn.commit()

# =========================================================
# ASTRO DATA
# =========================================================

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini",
    "Mrigashira", "Ardra", "Punarvasu", "Pushya",
    "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra",
    "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# =========================================================
# MOON TRAITS
# =========================================================

MOON_TRAITS = {

    "Aries": "jaldi decisions lene wale aur impatient nature",

    "Taurus": "stable aur practical thinking",

    "Gemini": "overthinking aur dual thinking tendency",

    "Cancer": "emotionally sensitive aur caring nature",

    "Leo": "self respect aur leadership tendency",

    "Virgo": "detail-oriented aur mentally active nature",

    "Libra": "balance aur relationship-focused thinking",

    "Scorpio": "andar emotions rakhne ki tendency",

    "Sagittarius": "growth aur freedom-oriented mindset",

    "Capricorn": "responsibility aur pressure carrying nature",

    "Aquarius": "different thinking aur detached observation",

    "Pisces": "deep emotional aur intuitive nature"
}

# =========================================================
# DASHA ENGINE
# =========================================================

DASHAS = [
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
    "Ketu",
    "Venus"
]

DASHA_EFFECTS = {

    "Sun": "self focus aur leadership learning phase",

    "Moon": "emotionally sensitive aur unstable phase",

    "Mars": "aggressive decisions aur action-oriented phase",

    "Rahu": "confusion aur unpredictable situations ka phase",

    "Jupiter": "growth aur guidance support phase",

    "Saturn": "hard work, delay aur responsibility phase",

    "Mercury": "career aur business thinking strong phase",

    "Ketu": "detachment aur internal confusion phase",

    "Venus": "relationship aur comfort-oriented phase"
}

# =========================================================
# DATE/TIME PARSER
# =========================================================

def normalize_date(date_str):

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%d %m %Y"
    ]

    for fmt in formats:

        try:

            dt = datetime.strptime(
                date_str.strip(),
                fmt
            )

            return dt.strftime("%d-%m-%Y")

        except:
            pass

    return None

def normalize_time(time_str):

    formats = [
        "%H:%M",
        "%I:%M %p",
        "%I %p",
        "%H.%M"
    ]

    for fmt in formats:

        try:

            dt = datetime.strptime(
                time_str.strip().upper(),
                fmt
            )

            return dt.strftime("%H:%M")

        except:
            pass

    return None

# =========================================================
# DASHA CALCULATION
# =========================================================

def calculate_dasha(dob):

    try:

        birth_year = int(
            dob.split("-")[2]
        )

        dasha_index = birth_year % len(DASHAS)

        current_dasha = DASHAS[dasha_index]

        dasha_effect = DASHA_EFFECTS[current_dasha]

        return current_dasha, dasha_effect

    except:

        return (
            "Saturn",
            "hard work aur slow timing phase"
        )

# =========================================================
# ASTROLOGY ENGINE
# =========================================================

def calculate_astrology(dob, tob):

    try:

        date_obj = datetime.strptime(
            f"{dob} {tob}",
            "%d-%m-%Y %H:%M"
        )

        jd = swe.julday(
            date_obj.year,
            date_obj.month,
            date_obj.day,
            date_obj.hour + date_obj.minute / 60
        )

        moon_long = swe.calc_ut(
            jd,
            swe.MOON
        )[0][0]

        moon_sign = SIGNS[int(moon_long / 30)]

        nak_index = int(
            moon_long / (13 + 1/3)
        )

        nakshatra = NAKSHATRAS[nak_index]

        houses = swe.houses(
            jd,
            26.9124,
            75.7873,
            b'P'
        )

        ascendant = houses[1][0]

        lagna = SIGNS[int(ascendant / 30)]

        career_house = SIGNS[
            (SIGNS.index(lagna) + 9) % 12
        ]

        relationship_house = SIGNS[
            (SIGNS.index(lagna) + 6) % 12
        ]

        money_house = SIGNS[
            (SIGNS.index(lagna) + 1) % 12
        ]

        current_dasha, dasha_effect = calculate_dasha(dob)

        personality = MOON_TRAITS.get(
            moon_sign,
            "emotionally observant nature"
        )

        return {

            "moon_sign": moon_sign,

            "nakshatra": nakshatra,

            "lagna": lagna,

            "career_house": career_house,

            "relationship_house": relationship_house,

            "money_house": money_house,

            "dasha": current_dasha,

            "dasha_effect": dasha_effect,

            "personality": personality
        }

    except Exception as e:

        print("ASTRO ERROR:", e)

        return None

# =========================================================
# TOPIC DETECTION
# =========================================================

def detect_topic(user_message):

    msg = user_message.lower()

    if any(word in msg for word in [
        "business",
        "money",
        "finance",
        "income",
        "loss",
        "debt"
    ]):
        return "business"

    elif any(word in msg for word in [
        "relationship",
        "love",
        "marriage",
        "partner",
        "breakup"
    ]):
        return "relationship"

    elif any(word in msg for word in [
        "career",
        "job",
        "promotion",
        "work"
    ]):
        return "career"

    elif any(word in msg for word in [
        "stress",
        "fear",
        "tension",
        "anxiety",
        "depression"
    ]):
        return "emotional"

    return "general"

# =========================================================
# EMOTIONAL DETECTION
# =========================================================

def detect_emotion(user_message):

    msg = user_message.lower()

    if any(word in msg for word in [
        "stress",
        "anxiety",
        "fear",
        "tension",
        "worried"
    ]):
        return "anxious"

    elif any(word in msg for word in [
        "sad",
        "hurt",
        "alone"
    ]):
        return "emotional"

    elif any(word in msg for word in [
        "angry",
        "frustrated"
    ]):
        return "frustrated"

    return "normal"

# =========================================================
# LIFE PATTERN
# =========================================================

def get_life_pattern(topic):

    patterns = {

        "business": [
            "Financial pressure mentally kaafi heavy feel hua hoga.",
            "Effort ke comparison mein growth slow feel hui hogi."
        ],

        "relationship": [
            "Emotionally misunderstandings ka phase strong raha lagta hai.",
            "Trust aur communication dono impact hue lagte hain."
        ],

        "career": [
            "Career mein delay aur slow recognition ka pattern dikh raha hai.",
            "Hard work ka result late milne ki tendency rahi lagti hai."
        ],

        "emotional": [
            "Mind ko kaafi pressure aur overthinking handle karna pada hai.",
            "Emotionally rest kam mila lagta hai."
        ],

        "general": [
            "Responsibility aur mental pressure kaafi strong raha hai.",
            "Life ne recent years mein kaafi maturity di lagti hai."
        ]
    }

    return random.choice(patterns[topic])

# =========================================================
# CHART SUMMARY
# =========================================================

def generate_chart_summary(name, astro):

    return f"""
✨ Kundali ready ho gayi hai, {name}.

🌙 Moon Sign: {astro['moon_sign']}
⭐ Nakshatra: {astro['nakshatra']}
⬆️ Lagna: {astro['lagna']}

💼 Career Energy: {astro['career_house']}
❤️ Relationship Energy: {astro['relationship_house']}
💰 Money Energy: {astro['money_house']}

🪐 Current Mahadasha: {astro['dasha']}

Aap mein {astro['personality']} strong dikh raha hai.

Current phase:
{astro['dasha_effect']}

Ab aap career, money, relationship, future ya current phase ke baare mein pooch sakte ho.
"""

# =========================================================
# AI ENGINE
# =========================================================

def ask_ai(user_message, astro_data, last_topic, last_question):

    topic = detect_topic(user_message)

    emotion = detect_emotion(user_message)

    life_pattern = get_life_pattern(topic)

    memory_line = ""

    if last_topic == topic:

        memory_line += """
User repeatedly discussing same concern.
Acknowledge ongoing pressure naturally.
"""

    if last_question:

        memory_line += f"""
Previous concern:
{last_question}
"""

    system_prompt = f"""
You are Jyotish Guruji.

You are experienced Indian astrologer.

Moon Sign:
{astro_data['moon_sign']}

Nakshatra:
{astro_data['nakshatra']}

Lagna:
{astro_data['lagna']}

Current Mahadasha:
{astro_data['dasha']}

Mahadasha Effect:
{astro_data['dasha_effect']}

Personality:
{astro_data['personality']}

Life Pattern:
{life_pattern}

Current Emotion:
{emotion}

{memory_line}

IMPORTANT RULES:

- Use natural Hinglish
- Sound human
- Sound emotionally observant
- Speak like experienced WhatsApp astrologer
- Keep replies short
- Use conversational rhythm
- Avoid textbook astrology
- Avoid over-explaining zodiac logic
- No essays
- No fake spirituality
- Use pauses naturally
- Some replies observational
- Some predictive
- Some emotional
- Some guiding
- Sometimes ask small reflective questions
- Mention current phase naturally
- Sound emotionally personal

GOOD STYLE:

"Hmm... pressure kaafi time se chal raha hai."

"Situation permanently blocked nahi lag rahi."

"Emotionally thakan build ho gayi lagti hai."

"Timing expected support nahi de rahi abhi."

Most replies:
2-5 short lines only.
"""

    try:

        response = requests.post(
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "temperature": 0.75,
                "max_tokens": 180
            },
            timeout=60
        )

        data = response.json()

        return (
            data["choices"][0]["message"]["content"],
            topic,
            emotion
        )

    except Exception as e:

        print("AI ERROR:", e)

        return (
            "🙏 Guruji abhi situation clearly dekh nahi paa rahe.",
            topic,
            emotion
        )

# =========================================================
# START
# =========================================================

@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        """
🙏 Namaste.

Apni birth details friendly format mein bhejiye.

Examples:

Vikas, 07-07-1985, 19:40, Ajmer

Vikas, 07/07/1985, 7:40 PM, Ajmer
"""
    )

# =========================================================
# MAIN CHAT
# =========================================================

@dp.message()
async def chat(message: Message):

    text = message.text.strip()

    parts = text.split(",")

    # =====================================================
    # NEW USER PROFILE
    # =====================================================

    if len(parts) >= 4:

        name = parts[0].strip()

        dob = normalize_date(parts[1])

        tob = normalize_time(parts[2])

        city = parts[3].strip()

        if not dob or not tob:

            await message.answer(
                """
🙏 Details samajh nahi aayi.

Example:

Vikas, 07-07-1985, 19:40, Ajmer

ya

Vikas, 07/07/1985, 7:40 PM, Ajmer
"""
            )

            return

        astro = calculate_astrology(
            dob,
            tob
        )

        if not astro:

            await message.answer(
                "🙏 Kundali calculate nahi ho paayi."
            )

            return

        cursor.execute("""
        INSERT OR REPLACE INTO users
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            message.chat.id,

            name,

            dob,

            tob,

            city,

            astro["moon_sign"],

            astro["nakshatra"],

            astro["lagna"],

            astro["career_house"],

            astro["relationship_house"],

            astro["money_house"],

            astro["dasha"],

            astro["dasha_effect"],

            astro["personality"],

            "",

            "",

            "normal"
        ))

        conn.commit()

        summary = generate_chart_summary(
            name,
            astro
        )

        await message.answer(summary)

        return

    # =====================================================
    # EXISTING USER
    # =====================================================

    cursor.execute(
        "SELECT * FROM users WHERE chat_id=?",
        (message.chat.id,)
    )

    user = cursor.fetchone()

    if not user:

        await message.answer(
            """
🙏 Pehle birth details bhejiye.

Example:

Vikas, 07-07-1985, 19:40, Ajmer
"""
        )

        return

    astro_data = {

        "moon_sign": user[5],

        "nakshatra": user[6],

        "lagna": user[7],

        "career_house": user[8],

        "relationship_house": user[9],

        "money_house": user[10],

        "dasha": user[11],

        "dasha_effect": user[12],

        "personality": user[13]
    }

    last_topic = user[14]

    last_question = user[15]

    await asyncio.sleep(
        random.uniform(1, 2)
    )

    reply, detected_topic, emotion = ask_ai(
        text,
        astro_data,
        last_topic,
        last_question
    )

    cursor.execute(
        """
        UPDATE users
        SET last_topic=?,
            last_question=?,
            emotional_state=?
        WHERE chat_id=?
        """,
        (
            detected_topic,
            text,
            emotion,
            message.chat.id
        )
    )

    conn.commit()

    await message.answer(reply)

# =========================================================
# MAIN
# =========================================================

async def main():

    print("🕉️ Jyotish Guruji Ultimate Running...")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
