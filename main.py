import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from openai import AsyncOpenAI


BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

dp = Dispatcher(storage=MemoryStorage())

client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Найти способ заработать")],
        [KeyboardButton(text="💡 Разобрать мою идею")],
        [KeyboardButton(text="📋 Мой план")],
        [KeyboardButton(text="👤 Профиль")],
    ],
    resize_keyboard=True
)

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


async def ask_ai(prompt: str) -> str:
    if not client:
        return (
            "⚠️ AI пока не подключён.\n\n"
            "Добавь переменную OPENAI_API_KEY в настройках RelaxDev."
        )

    try:
        response = await client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )
        return response.output_text
    except Exception as e:
        logging.exception("AI error")
        return f"❌ Ошибка AI: {str(e)}"


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "🤖 <b>AI ЗАРАБОТОК</b>\n\n"
        "Я помогу найти реальные способы заработка "
        "под твои возможности.\n\n"
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

    await message.answer("🤖 Анализирую твои возможности...")

    prompt = f"""
Ты — эксперт по поиску способов заработка.

Данные пользователя:
Цель: {data['goal']}
Время: {data['time']}
Ресурсы: {data['resources']}
Формат: {data['format']}

Подбери 3 конкретных способа заработка.

Для каждого обязательно укажи:
1. Название
2. Что именно делать
3. Реалистичный потенциальный доход
4. Сколько нужно денег для старта
5. Где искать клиентов
6. Первые 3 шага
7. Главные риски

Не предлагай абстрактные советы вроде "займись фрилансом".
Предложения должны быть реально выполнимыми с указанными ресурсами.

Ответ на русском языке.
"""

    result = await ask_ai(prompt)

    await message.answer(
        "🎯 <b>Вот что я нашёл:</b>\n\n" + result,
        reply_markup=main_menu
    )


@dp.message(F.text == "💡 Разобрать мою идею")
async def idea(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "💡 Напиши свою идею заработка одним сообщением.\n\n"
        "Например:\n"
        "Хочу делать Telegram-ботов и продавать их бизнесу."
    )


@dp.message(F.text == "📋 Мой план")
async def plan(message: Message):
    await message.answer(
        "📋 <b>Мой план</b>\n\n"
        "Система сохранения планов будет добавлена следующим этапом."
    )


@dp.message(F.text == "👤 Профиль")
async def profile(message: Message):
    await message.answer(
        f"👤 <b>Профиль</b>\n\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"👤 Имя: {message.from_user.first_name}"
    )


@dp.message()
async def free_text(message: Message):
    if not client:
        await message.answer(
            "⚠️ AI пока не подключён.\n\n"
            "Добавь OPENAI_API_KEY в RelaxDev."
        )
        return

    await message.answer("🤖 Анализирую...")

    prompt = f"""
Пользователь предложил идею заработка:

{message.text}

Проанализируй её как бизнес-идею.

Дай:
💰 Потенциал заработка
📈 Спрос
💸 Стартовые расходы
🎯 Кто клиент
🔎 Где искать клиентов
⚠️ Риски
🚀 Как запустить
🔥 Что изменить, чтобы повысить шансы на успех

Будь конкретным и честным.
Ответ на русском языке.
"""

    result = await ask_ai(prompt)

    await message.answer(
        "💡 <b>Разбор идеи</b>\n\n" + result,
        reply_markup=main_menu
    )


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден!")

    bot = Bot(token=BOT_TOKEN)

    logging.info("🤖 AI Заработок запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())