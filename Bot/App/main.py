import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.filters import CommandStart
from aiogram.filters import Command
from config import BOT_TOKEN
from msg import msgbot



# Создаем экземпляр диспетчера
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(msgbot.start_message())

@dp.message(Command("r"))
async def stop_command(message: types.Message):
    await message.answer("stop")

# Запуск бота
async def main():
    # Создаем экземпляр бота
    bot = Bot(token=BOT_TOKEN)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())