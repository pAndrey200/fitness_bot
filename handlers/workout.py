# handlers/workout.py

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from data import users
from states import WorkoutStates
from services import ensure_logs_for_today
from handlers.start import get_main_menu

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "Log Workout")
async def workout_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль /set_profile.")
        return

    await message.answer("Какой тип тренировки? (например, 'бег', 'йога' и т.д.)")
    await state.set_state(WorkoutStates.waiting_for_type)

@router.message(WorkoutStates.waiting_for_type)
async def workout_type_received(message: Message, state: FSMContext):
    workout_type = message.text.strip()
    await state.update_data(workout_type=workout_type)

    await message.answer("Сколько минут длилась тренировка? (введите число)")
    await state.set_state(WorkoutStates.waiting_for_minutes)

@router.message(WorkoutStates.waiting_for_minutes)
async def workout_minutes_received(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль /set_profile.")
        await state.clear()
        return

    data = await state.get_data()
    workout_type = data.get("workout_type", "тренировка")

    try:
        minutes = float(message.text)
    except ValueError:
        await message.answer("Укажите время в минутах (числом). Например, 30.")
        return

    # Примерная формула: 10 ккал / мин
    burned = 10.0 * minutes

    ensure_logs_for_today(user_id)
    today_str = list(users[user_id]["logs"].keys())[-1]
    users[user_id]["logs"][today_str]["burned_cal"] += burned

    # Доп совет по воде
    blocks = int(minutes // 30)
    extra_water = 200 * blocks

    txt = (
        f"Тренировка: {workout_type}, {minutes} мин.\n"
        f"Сожжено ~{burned:.0f} ккал.\n"
    )
    if extra_water > 0:
        txt += f"Рекомендуется дополнительно выпить {extra_water} мл воды."
    else:
        txt += "Не забывайте пить воду!"

    await message.answer(txt, reply_markup=get_main_menu())

    await state.clear()
