import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import TELEGRAM_TOKEN
from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.food import router as food_router
from handlers.water import router as water_router
from handlers.workout import router as workout_router
from handlers.progress import router as progress_router

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(food_router)
    dp.include_router(workout_router)
    dp.include_router(progress_router)
    dp.include_router(water_router)
    
    

    logger.info("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
