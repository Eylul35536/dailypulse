import aiohttp
import os
import asyncio
import random
import base64
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

from openai import OpenAI

# ======================
# ENV
# ======================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
N8N_WEBHOOK = os.getenv("N8N_WEBHOOK")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not BOT_TOKEN or not OPENAI_KEY:
    raise RuntimeError("ENV missing (BOT_TOKEN / OPENAI_API_KEY)")

# ======================
# INIT
# ======================
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_KEY)

# ======================
# /start (ESKİ GİRİŞ)
# ======================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Hello 👋\n\n"
        "Commands:\n"
        "/news – News summary\n"
        "/motivate – Motivation\n"
        "/fact – Random fact\n"
        "/weather – Weather\n\n"
        "📸 Send a photo for image analysis.\n"
        "💬 Or just write anything and I will reply.\n"
        "🍽 If you mention food/calories, it will be saved."
    )
# ======================
# /fact
# ======================
@dp.message(Command("fact"))
async def fact(message: types.Message):
    facts = [
        "Honey never spoils.",
        "Octopuses have three hearts.",
        "Bananas are berries.",
        "A day on Venus is longer than a year.",
        "Sharks existed before trees."
    ]
    await message.answer(random.choice(facts))
# ======================
# /weather
# ======================

@dp.message(Command("weather"))
async def weather(message: types.Message):
    if not WEATHER_API_KEY:
        await message.answer("⚠️ Weather API key is missing.")
        return

    city = "Warsaw"
    url = (
    f"https://api.openweathermap.org/data/2.5/weather"
    f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
    except:
        await message.answer("⚠️ Weather service unavailable.")
        return

    if "main" not in data:
        await message.answer("❌ Could not fetch weather.")
        return

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"].title()

    await message.answer(
        f"🌤 Weather in {city}\n"
        f"🌡 Temperature: {temp}°C\n"
        f"📝 Condition: {desc}"
    )
# ======================
# NEWS
# ======================
@dp.message(Command("news"))
async def news(message: types.Message):
    sample = [
        "🌍 Global markets show positive movement.",
        "🚀 SpaceX launched a new satellite.",
        "📱 Apple working on new AI features.",
        "🏢 Remote work expands across tech sector.",
        "🌡️ Climate experts warn about extreme heat.",
        "🎮 New gaming consoles dominate the holiday season.",
        "⚽ Top football leagues announce mid-season transfers.",
        "💼 Remote work continues to reshape office culture."
    ]
    news_text = "📰 <b>Today's News</b>\n" + "\n".join(random.sample(sample, 3))
    await message.answer(news_text)
# ======================
# IMAGE ANALYSIS (STABLE)
# ======================
@dp.message(F.photo)
async def image_recognition(message: types.Message):
    await message.answer("📸 Analyzing the photo...")

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    data = await bot.download_file(file.file_path)

    img_b64 = base64.b64encode(data.read()).decode()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image clearly in simple English."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}"
                            }
                        }
                    ]
                }
            ]
        )

        answer = response.choices[0].message.content
        await message.answer(answer)

    except Exception as e:
        print("VISION ERROR:", e)
        await message.answer("⚠️ I couldn't analyze the photo.")

# ======================
# TEXT CHAT
# ===================
@dp.message(F.text)
async def chat(message: types.Message):
    text = message.text

    # ---- AI PARSE (5 DK ÇÖZÜM) ----
    parse_prompt = f"""
Extract meal info from this message.
Return ONLY valid JSON.

Message:
"{text}"

JSON format:
{{
  "food": string or null,
  "amount": number or null,
  "unit": string or null,
  "calories": number or null
}}
"""

    try:
        parse_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract structured meal data."},
                {"role": "user", "content": parse_prompt}
            ]
        )

        parsed = parse_resp.choices[0].message.content
    except:
        parsed = "{}"

    # ---- N8N WEBHOOK ----
    if N8N_WEBHOOK:
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    N8N_WEBHOOK,
                    json={
                        "user_id": message.from_user.id,
                        "raw_text": text,
                        "parsed": parsed
                    }
                )
        except Exception as e:
            print("n8n error:", e)

    # ---- NORMAL CHAT (BOZULMADI) ----
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly assistant."},
                {"role": "user", "content": text}
            ]
        )
        await message.answer(response.choices[0].message.content)
    except:
        await message.answer("⚠️ AI error.")

    await message.answer("📌 Meal saved 💾")

# ======================
# RUN
# ======================
async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

