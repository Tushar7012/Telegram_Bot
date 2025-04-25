import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from groq import Groq

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Reference class to store last assistant response
class Reference:
    def __init__(self):
        self.reference = ""

reference = Reference() 
model_name = "llama3-70b-8192"

# Setup bot
bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# Clear chat history
def clear_past():
    reference.reference = ""
    logging.info("Cleared the conversation history")

@dp.message(Command(commands=["clear"]))
async def clear_command(message: types.Message):
    clear_past()
    await message.answer("I've cleared the conversation history. You can start a new conversation now.")

@dp.message(Command(commands=["start"]))
async def start_command(message: types.Message):
    await message.answer("Hi 👋 I'm Ringo Bot!\nPowered by Tushar. How can I help you?")

@dp.message(Command(commands=["help"]))
async def help_command(message: types.Message):
    help_text = """
    Hi there 👋! I'm Ringo Bot, your friendly assistant powered by Tushar.
    /start - Start the conversation
    /clear - Clear the conversation history 
    /help - Show this help menu
    """
    await message.reply(help_text)

@dp.message(F.text)
async def chat_with_groq(message: types.Message):
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "assistant", "content": reference.reference},
            {"role": "user", "content": message.text}
        ]
    )
    reference.reference = response.choices[0].message.content
    await bot.send_message(chat_id=message.chat.id, text=reference.reference)
    logging.info(f"Sent message: {reference.reference}")

# Main entry point
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
