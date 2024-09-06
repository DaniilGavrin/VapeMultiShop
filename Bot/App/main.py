import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN
from msg import msgbot

is_catalog = 0
is_profile = 0

# Создаем экземпляр диспетчера
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Каталог",
        callback_data="catalog")
    )
    builder.add(types.InlineKeyboardButton(
        text="Мой профиль",
        callback_data="profile")
    )
    await message.answer(msgbot.start_message(), reply_markup=builder.is_markup())

@dp.message(Command("r"))
async def stop_command(message: types.Message):
    await message.answer("stop")

# TODO: Создать логику каталога
@dp.callback_query(F.data == "catalog")
async def catalog(message: types.Message):
    if is_catalog == 0:
        await message.answer("Каталог ещё не создан и не существует или админ даун забыл тест убрать")

@dp.callback_query(F.data == "profile")
async def catalog(message: types.Message):
    if is_profile == 0:
        await message.answer("Профиль ещё не создан и не существует или админ даун забыл тест убрать")

# Запуск бота
async def main():
    # Создаем экземпляр бота
    bot = Bot(token=BOT_TOKEN)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())