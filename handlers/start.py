
import logging
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from data import users

router = Router()
logger = logging.getLogger(__name__)

def get_main_menu() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Log Water"), KeyboardButton(text="Log Food")],
        [KeyboardButton(text="Log Workout"), KeyboardButton(text="Check Progress")],
        [KeyboardButton(text="Show Graph")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {
            "weight": 70,
            "height": 170,
            "age": 25,
            "activity": 30,
            "city": "Moscow",
            "daily_water_goal": 2000,
            "daily_cal_goal": 2500,
            "logs": {}
        }

    await message.answer(
        "Привет! Я твой фитнес-бот.\n"
        "Могу помочь с нормой воды и калорий, а также вести учёт прогресса.\n"
        "Для детальной настройки профиля используйте /set_profile.\n",
        reply_markup=get_main_menu()
    )
