import os
import asyncio
import random
import aiohttp
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

from openai import AsyncOpenAI
import base64

# Load .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
WEATHER_API = os.getenv("WEATHER_API")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Initialize
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_KEY)


# -------------------------
# /start
# -------------------------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"Hello {message.from_user.full_name}! 👋\n\n"
        "Commands:\n"
        "/news – News summary\n"
        "/motivate – Motivation\n"
        "/fact – Random fact\n"
        "/weather – Weather\n"
        "📸 Send a PHOTO for image analysis."
    )


# -------------------------
# /news
# -------------------------
@dp.message(Command("news"))
async def news(message: types.Message):
    sample = [
        "🌍 Global markets show positive movement.",
        "🚀 SpaceX launched a new satellite.",
        "📱 Apple working on new AI features.",
        "🏢 Remote work expands across tech sector.",
        "🌡 Climate experts warn about extreme heat."
    ]
    text = "📰 <b>Today's News</b>\n" + "\n".join(random.sample(sample, 3))
    await message.answer(text)


# -------------------------
# /motivate
# -------------------------
@dp.message(Command("motivate"))
async def motivate(message: types.Message):
    motivations = [
        "✨ Believe in yourself.",
        "🔥 Small steps lead to big wins.",
        "🌟 Every day is a chance to grow.",
        "💡 Your potential is limitless.",
        "🏆 Keep going — you're doing great!"
    ]
    await message.answer(random.choice(motivations))


# -------------------------
# IMAGE RECOGNITION (Aiogram v3)
# -------------------------
@dp.message(F.photo)
async def image_recognition(message: types.Message):
    await message.answer("📸 Analyzing your image...")

    # Last photo
    photo = message.photo[-1]

    # Download
    file = await bot.get_file(photo.file_id)
    data = await bot.download_file(file.file_path)

    # Base64 encode
    img_b64 = base64.b64encode(data.read()).decode()

    # OpenAI Vision correct format
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image simply."},
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

    description = response.choices[0].message.content
    await message.answer(f"📝 <b>Description:</b>\n{description}")
# -------------------------
# /fact
# -------------------------
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


# -------------------------
# /weather
# -------------------------
@dp.message(Command("weather"))
async def weather(message: types.Message):
    if not WEATHER_API:
        await message.answer("⚠️ WEATHER_API key missing in .env!")
        return

    city = "Warsaw"
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_API}&units=metric"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
    except:
        await message.answer("⚠️ Weather service unavailable.")
        return

    if data.get("main"):
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].title()
        await message.answer(
            f"🌤 <b>Weather in {city}</b>\n"
            f"🌡 Temp: <b>{temp}°C</b>\n"
            f"📝 Condition: <b>{desc}</b>"
        )
    else:
        await message.answer("❌ Could not fetch weather.")


# -------------------------
# Run bot
# -------------------------
async def main():
    print("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

