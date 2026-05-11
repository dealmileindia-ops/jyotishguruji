import asyncio
import random
import os

import google.generativeai as genai
from dotenv import load_dotenv

from services.memory import get_memory
from prompts.guru import PROMPTS

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-1.5-flash")

async def guru_reply(user_id, text, language="en"):

    memories = get_memory(user_id)

    await asyncio.sleep(random.uniform(2,4))

    prompt = f'''
{PROMPTS.get(language)}

Previous emotional memories:
{memories}

User:
{text}

Reply naturally like a real Indian astro guru.
Avoid robotic tone.
Use emotional intuition.
'''

    response = model.generate_content(prompt)

    return response.text
