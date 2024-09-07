import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from config import BOT_TOKEN
from msg import msgbot
from api import API

is_catalog = 0
is_profile = 0
is_accept = 1
is_cart = 0


# Создаем экземпляр диспетчераp
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔞 Мне есть 18 лет", callback_data="accept_user")]])
    
    await message.answer(msgbot.start_message(), reply_markup=keyboard)


@dp.message(Command("menu"))
async def send(message: types.Message):
    # Создание клавиатуры с двумя кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Профиль", callback_data="profile")],
        [InlineKeyboardButton(text="Каталог", web_app=WebAppInfo(url="https://bytewizard.ru/"))],
        [InlineKeyboardButton(text="Корзина", callback_data="cart")],
        [InlineKeyboardButton(text="Ваши заказы", callback_data="myorder")]
    ])

    # Отправка сообщения с клавиатурой
    await message.answer("Выберите опцию:", reply_markup=keyboard)
    
@dp.callback_query(F.data == "cart")
async def cart(message: types.Message):
    if is_cart == 0:
        await message.answer("Корзина ещё не создана и не существует или админ даун забыл тест убрать")
        return

# TODO: Сделать логику профиля
@dp.callback_query(F.data == "profile")
async def profile(callback_query: types.CallbackQuery):
        if is_profile == 0:
            await callback_query.message.answer("Профиль ещё не создан и не существует или админ даун забыл тест убрать") # type: ignore

        user_id = callback_query.from_user.id
        username = callback_query.from_user.username
        print(user_id)
        # TODO: Отправить информацию о профиле
        user = API.get_profile(user_id)
        value = user.get("value")
        all_order = user.get("all_order")
        await callback_query.message.answer(f"Ваш id {user_id}.\nВаш username {username}\nВы купили на {value}RUB\nКоличество заказов {all_order}.\n")

@dp.callback_query(F.data == "accept_user")
async def access_user(callback_query: types.CallbackQuery):
    # Проверка, если функция не готова
    if is_accept == 0:
        await callback_query.answer("Функция не готова!")
        return

    # Получение user_id и username
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    print(f"User ID: {user_id}, Username: {username}")

    
    await callback_query.message.answer(f"User ID: {user_id}, Username: {username}. Введите /menu для доступа к меню бота")

# Запуск бота
async def main():
    # Создаем экземпляр бота
    bot = Bot(token=BOT_TOKEN)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())