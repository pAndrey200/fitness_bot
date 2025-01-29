import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from data import users
from states import WaterStates
from services import ensure_logs_for_today
from handlers.start import get_main_menu

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "Log Water")
async def water_start(message: Message, state: FSMContext):
    """
    Пользователь нажал кнопку "Log Water" (ReplyKeyboard).
    Запускаем FSM: просим ввести кол-во мл.
    """
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль /set_profile.")
        return

    await message.answer("Сколько мл воды вы выпили? (Введите число)")
    await state.set_state(WaterStates.waiting_for_amount)

@router.message(WaterStates.waiting_for_amount)
async def water_amount_received(message: Message, state: FSMContext):
    """
    Пользователь ввёл кол-во воды (мл).
    """
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль /set_profile.")
        await state.clear()
        return

    try:
        ml = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число (мл). Например 250.")
        return

    ensure_logs_for_today(user_id)
    today_str = list(users[user_id]["logs"].keys())[-1]
    users[user_id]["logs"][today_str]["water"] += ml

    current_water = users[user_id]["logs"][today_str]["water"]
    goal = users[user_id]["daily_water_goal"]
    left = max(0, goal - current_water)

    await message.answer(
        f"Записано {ml:.0f} мл воды.\n"
        f"Сегодня: {current_water:.0f} / {goal:.0f} мл.\n"
        f"Осталось: {left:.0f} мл.",
        reply_markup=get_main_menu()
    )

    await state.clear()
