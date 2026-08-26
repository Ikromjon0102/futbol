import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Telegram Bot Tokeningizni quyidagi o'zgaruvchiga kiriting
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "BOT_TOKENINGIZNI_SHU_YERGA_YOZING")

# Agar dasturni serverga joylashtirsangiz (masalan Render, Railway yoki Ngrok) o'sha URL manzilni yozasiz
# Hozircha localhost / webapp misoli:
WEB_APP_URL = os.environ.get("WEB_APP_URL", "http://localhost:8000")

dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    webapp_btn = InlineKeyboardButton(
        text="⚽ Futbol Ilovasini Ochish",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[webapp_btn]])

    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>! 👋\n\n"
        f"🏆 <b>Futbol - O'yinlar va Jadvallar</b> ilovasiga xush kelibsiz!\n\n"
        f"Ushbu bot orqali siz:\n"
        f"• APL, La Liga, Turkiya, A Seriya o'yinlari va jadvallarini;\n"
        f"• 🇺🇿 Eldor Shomurodov va Abbos Fayzullayev natijalarini;\n"
        f"• Toshkent vaqti bilan boshlanish soatlarini ko'rishingiz mumkin.\n\n"
        f"Quyidagi tugmani bosing 👇",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def main():
    if BOT_TOKEN == "BOT_TOKENINGIZNI_SHU_YERGA_YOZING":
        print("⚠️ Iltimos, telegram_bot.py fayliga @BotFather dan olgan BOT_TOKENingizni kiriting.")
        return

    bot = Bot(token=BOT_TOKEN)
    print("🤖 Telegram Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
