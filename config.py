import os
from dotenv import load_dotenv

load_dotenv()  

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

