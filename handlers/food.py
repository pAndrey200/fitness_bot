import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import FoodStates
from data import users
from services import ensure_logs_for_today, get_nutritionix_calories
from handlers.start import get_main_menu

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "Log Food")
async def log_food_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль (/set_profile).")
        return

    await message.answer("Введите название продукта (на английском).")
    await state.set_state(FoodStates.waiting_for_product)

@router.message(FoodStates.waiting_for_product)
async def food_entered(message: Message, state: FSMContext):
    product_name = message.text.strip()
    cal_100g = get_nutritionix_calories(product_name)

    await state.update_data(product_name=product_name, cal_100g=cal_100g)

    if cal_100g <= 0:
        await message.answer(
            f"Не удалось найти калорийность для '{product_name}'. Повторите попытку.",
            reply_markup=get_main_menu()
        )
        await state.clear()
        return

    await message.answer(
        f"Продукт '{product_name}' ~ {cal_100g:.1f} ккал на 100 г.\n"
        "Сколько грамм вы съели? (число)"
    )
    await state.set_state(FoodStates.waiting_for_grams)

@router.message(FoodStates.waiting_for_grams)
async def food_grams_entered(message: Message, state: FSMContext):
    """
    Получаем кол-во граммов, считаем ккал, записываем.
    """
    user_id = message.from_user.id
    data = await state.get_data()
    product_name = data["product_name"]
    cal_100g = data["cal_100g"]

    try:
        grams = float(message.text)
    except ValueError:
        await message.answer("Введите число грамм (например, 120).", reply_markup=get_main_menu())
        await state.clear()
        return

    total_cal = (cal_100g / 100.0) * grams

    ensure_logs_for_today(user_id)
    today_str = list(users[user_id]["logs"].keys())[-1]
    users[user_id]["logs"][today_str]["food_cal"] += total_cal

    await message.answer(
        f"Добавлено ~{total_cal:.1f} ккал из '{product_name}'.\n"
        f"Всего сегодня: {users[user_id]['logs'][today_str]['food_cal']:.1f} ккал.",
        reply_markup=get_main_menu()
    )
    await state.clear()
