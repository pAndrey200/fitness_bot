import logging
import requests
import datetime
import io
import matplotlib.pyplot as plt

from config import NUTRITIONIX_APP_ID, NUTRITIONIX_API_KEY, OPENWEATHER_API_KEY
from data import users

logger = logging.getLogger(__name__)

def get_date_str(date: datetime.date = None) -> str:
    if date is None:
        date = datetime.date.today()
    return date.isoformat()

def ensure_logs_for_today(user_id: int) -> None:
    if user_id not in users:
        return
    if "logs" not in users[user_id]:
        users[user_id]["logs"] = {}
    today_str = get_date_str()
    if today_str not in users[user_id]["logs"]:
        users[user_id]["logs"][today_str] = {
            "water": 0.0,
            "food_cal": 0.0,
            "burned_cal": 0.0
        }

def get_nutritionix_calories(product_name: str) -> float:
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "query": product_name,
    }
    resp = requests.post(url, headers=headers, json=payload)
    data = resp.json()

    foods = data.get("foods", [])
    if not foods:
        return 0.0

    # Берём первый продукт
    item = foods[0]
    calories = item.get("nf_calories", 0.0)
    return calories

def build_progress_chart(user_id: int, days: int = 7) -> io.BytesIO:
    if user_id not in users:
        return None

    logs = users[user_id].get("logs", {})
    water_goal = users[user_id].get("daily_water_goal", 2000)
    cal_goal = users[user_id].get("daily_cal_goal", 2500)

    # Составляем списки дат, воды, калорий и т.п.
    today = datetime.date.today()
    date_list = []
    water_vals = []
    water_goals = []
    food_vals = []
    cal_goals = []
    burned_vals = []

    # Прошлые дни: отсчёт от (days-1) до 0
    for i in range(days):
        d = today - datetime.timedelta(days=(days - 1 - i))
        d_str = d.isoformat()

        date_list.append(d_str[5:])  # "MM-DD"
        day_logs = logs.get(d_str, {"water": 0, "food_cal": 0, "burned_cal": 0})

        water_vals.append(day_logs["water"])
        water_goals.append(water_goal)
        food_vals.append(day_logs["food_cal"])
        burned_vals.append(day_logs["burned_cal"])
        cal_goals.append(cal_goal)

    fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(6, 8))
    fig.suptitle("Прогресс за последние 7 дней")

    # 1) Вода (ось X - date_list)
    axs[0].bar(date_list, water_vals, color='blue', alpha=0.7, label='Выпито (мл)')
    axs[0].plot(date_list, water_goals, color='red', label='Цель (мл)')
    axs[0].set_ylabel("Вода (мл)")
    axs[0].legend()
    axs[0].grid(True)

    # 2) Калории (потреблено vs цель, + burned как доп. линия)
    axs[1].bar(date_list, food_vals, color='green', alpha=0.7, label='Потреблено (ккал)')
    axs[1].plot(date_list, cal_goals, color='red', label='Цель (ккал)')
    axs[1].plot(date_list, burned_vals, color='orange', label='Сожжено (ккал)')
    axs[1].set_ylabel("Калории (ккал)")
    axs[1].legend()
    axs[1].grid(True)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    return buf

def get_weather_temp(city: str) -> float:
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
        resp = requests.get(url)
        data = resp.json()
        return float(data["main"]["temp"])
    except Exception as e:
        logger.error(f"Ошибка при запросе погоды: {e}")
        return 20.0

def calculate_water_goal(user_data: dict) -> float:
    weight = user_data["weight"]
    activity = user_data["activity"]
    city = user_data["city"]

    base = weight * 30
    activity_30min_units = int(activity // 30)
    activity_add = 500 * activity_30min_units

    temp = get_weather_temp(city)
    weather_add = 500 if temp > 25 else 0

    return base + activity_add + weather_add

def calculate_calorie_goal(user_data: dict) -> float:
    w = user_data["weight"]
    h = user_data["height"]
    a = user_data["age"]
    activity = user_data["activity"]

    base_cal = 10 * w + 6.25 * h - 5 * a
    blocks = int(activity // 30)
    activity_cal = 200 * blocks

    return base_cal + activity_cal