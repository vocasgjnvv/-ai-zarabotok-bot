import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher(storage=MemoryStorage())


# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Найти способ заработать")],
        [KeyboardButton(text="💡 Разобрать мою идею")],
        [KeyboardButton(text="📋 Мой план")],
        [KeyboardButton(text="👤 Профиль")],
    ],
    resize_keyboard=True
)


# Вопросы анкеты
goal_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 20 000 ₽")],
        [KeyboardButton(text="💰 50 000 ₽")],
        [KeyboardButton(text="💰 100 000 ₽")],
        [KeyboardButton(text="💰 200 000 ₽+")],
        [KeyboardButton(text="✏️ Своя сумма")],
    ],
    resize_keyboard=True
)


time_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏱ До 1 часа")],
        [KeyboardButton(text="⏱ 1–3 часа")],
        [KeyboardButton(text="⏱ 3–6 часов")],
        [KeyboardButton(text="🔥 Полный день")],
    ],
    resize_keyboard=True
)


resources_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Только телефон")],
        [KeyboardButton(text="💻 Компьютер")],
        [KeyboardButton(text="🚗 Автомобиль")],
        [KeyboardButton(text="💰 Есть капитал")],
        [KeyboardButton(text="🤷 Ничего")],
    ],
    resize_keyboard=True
)


format_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌐 Только онлайн")],
        [KeyboardButton(text="🏠 Только офлайн")],
        [KeyboardButton(text="🔄 Без разницы")],
    ],
    resize_keyboard=True
)


class EarningForm(StatesGroup):
    goal = State()
    time = State()
    resources = State()
    format = State()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "🤖 <b>AI ЗАРАБОТОК</b>\n\n"
        "Я помогу найти подходящий способ заработка "
        "с учётом твоей цели, времени и возможностей.\n\n"
        "Выбери действие 👇",
        reply_markup=main_menu
    )


@dp.message(F.text == "🚀 Найти способ заработать")
async def start_earning(message: Message, state: FSMContext):
    await state.set_state(EarningForm.goal)

    await message.answer(
        "🚀 <b>Начинаем поиск</b>\n\n"
        "Сколько ты хочешь зарабатывать в месяц?",
        reply_markup=goal_menu
    )


@dp.message(EarningForm.goal)
async def get_goal(message: Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await state.set_state(EarningForm.time)

    await message.answer(
        "⏱ Сколько времени ты готов уделять этому каждый день?",
        reply_markup=time_menu
    )


@dp.message(EarningForm.time)
async def get_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await state.set_state(EarningForm.resources)

    await message.answer(
        "🛠 Что у тебя есть для заработка?",
        reply_markup=resources_menu
    )


@dp.message(EarningForm.resources)
async def get_resources(message: Message, state: FSMContext):
    await state.update_data(resources=message.text)
    await state.set_state(EarningForm.format)

    await message.answer(
        "🌐 Какой формат заработка тебе подходит?",
        reply_markup=format_menu
    )


@dp.message(EarningForm.format)
async def get_format(message: Message, state: FSMContext):
    await state.update_data(format=message.text)

    data = await state.get_data()
    await state.clear()

    await message.answer(
        "🔎 <b>Анкета заполнена!</b>\n\n"
        f"🎯 Цель: {data['goal']}\n"
        f"⏱ Время: {data['time']}\n"
        f"🛠 Возможности: {data['resources']}\n"
        f"🌐 Формат: {data['format']}\n\n"
        "🤖 Теперь подключим AI и он подберёт "
        "3 подходящих способа заработка.",
        reply_markup=main_menu
    )


@dp.message(F.text == "💡 Разобрать мою идею")
async def idea(message: Message):
    await message.answer(
        "💡 Напиши свою идею заработка одним сообщением.\n\n"
        "Например:\n"
        "«Хочу делать Telegram-ботов и продавать их бизнесу»"
    )


@dp.message(F.text == "📋 Мой план")
async def plan(message: Message):
    await message.answer(
        "📋 <b>Твой план</b>\n\n"
        "Пока план не создан.\n"
        "Пройди 🚀 «Найти способ заработать»."
    )


@dp.message(F.text == "👤 Профиль")
async def profile(message: Message):
    await message.answer(
        f"👤 <b>Профиль</b>\n\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"👤 Имя: {message.from_user.first_name}"
    )


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден!")

    bot = Bot(token=BOT_TOKEN)

    print("🤖 AI Заработок запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())