import logging
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command

from data import users
from services import ensure_logs_for_today, build_progress_chart
from handlers.start import get_main_menu



router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "Check Progress")
async def check_progress(message: Message):
    """
    Показываем итоги за сегодня: вода, калории и т.д.
    """
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль /set_profile.")
        return

    ensure_logs_for_today(user_id)
    today_str = list(users[user_id]["logs"].keys())[-1]
    day_log = users[user_id]["logs"][today_str]

    water = day_log["water"]
    water_goal = users[user_id]["daily_water_goal"]

    food_cal = day_log["food_cal"]
    cal_goal = users[user_id]["daily_cal_goal"]

    burned = day_log["burned_cal"]
    balance = food_cal - burned

    text = (
        f"📊 Прогресс за {today_str}:\n\n"
        f"Вода: {water:.0f} / {water_goal:.0f} мл\n"
        f"Калории: потреблено {food_cal:.0f} / {cal_goal:.0f}, "
        f"сожжено {burned:.0f}, баланс {balance:.0f}.\n"
    )
    await message.answer(text, reply_markup=get_main_menu())


@router.message(F.text == "Show Graph")
async def show_graph(message: Message):
    """
    Отправляем график за последнюю неделю (7 дней).
    """
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Сначала настройте профиль.")
        return

    image_buf = build_progress_chart(user_id, days=7)
    if not image_buf:
        await message.answer("Нет данных для отображения графика.")
        return

    await message.answer_photo(
        photo=BufferedInputFile(image_buf.getvalue(), "chart.png"), 
        caption="Ваш прогресс по воде и калориям (за 7 дней).",
        reply_markup=get_main_menu()
    )
