import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from services import calculate_water_goal, calculate_calorie_goal
from data import users
from states import ProfileStates

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext):
    """
    Запуск настройки профиля - /set_profile
    Спрашиваем: вес (кг).
    """
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {
            "weight": 70,
            "height": 170,
            "age": 25,
            "city": "Moscow",
            "daily_water_goal": 2000,
            "daily_cal_goal": 2500,
            "logs": {}
        }

    await message.answer("Давайте настроим ваш профиль. Введите ваш вес (в кг):")
    await state.set_state(ProfileStates.weight)

@router.message(ProfileStates.weight)
async def process_weight(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        w = float(message.text)
        users[user_id]["weight"] = w
    except ValueError:
        await message.answer("Введите вес числом, например: 70")
        return

    await message.answer("Введите ваш рост (в см):")
    await state.set_state(ProfileStates.height)

@router.message(ProfileStates.height)
async def process_height(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        h = float(message.text)
        users[user_id]["height"] = h
    except ValueError:
        await message.answer("Введите рост числом, например: 170")
        return

    await message.answer("Введите ваш возраст (лет):")
    await state.set_state(ProfileStates.age)

@router.message(ProfileStates.age)
async def process_age(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        a = float(message.text)
        users[user_id]["age"] = a
    except ValueError:
        await message.answer("Введите возраст числом, например: 30")
        return

    await message.answer("Сколько минут активности у вас в день?")
    await state.set_state(ProfileStates.activity)


@router.message(ProfileStates.activity)
async def process_activity(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        activity = float(message.text)
        users[user_id]["activity"] = activity
    except ValueError:
        await message.answer("Введите число минут (например, 45).")
        return
    await message.answer("В каком городе вы находитесь?")
    await state.set_state(ProfileStates.city)

@router.message(ProfileStates.city)
async def process_city(message: Message, state: FSMContext):
    user_id = message.from_user.id
    city = message.text.strip()
    if city:
        users[user_id]["city"] = city

    w_goal = calculate_water_goal(users[user_id])
    c_goal = calculate_calorie_goal(users[user_id])
    users[user_id]["water_goal"] = w_goal
    users[user_id]["calorie_goal"] = c_goal
    users[user_id]["logged_water"] = 0
    users[user_id]["logged_calories"] = 0
    users[user_id]["burned_calories"] = 0

    await message.answer(
        "Профиль сохранён!\n"
        f"Вес: {users[user_id]['weight']} кг\n"
        f"Рост: {users[user_id]['height']} см\n"
        f"Возраст: {users[user_id]['age']} лет\n"
        f"Город: {users[user_id]['city']}\n\n"
        "Можете теперь использовать меню для логов и прогресса."
    )
    await state.clear()
