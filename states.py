from aiogram.fsm.state import State, StatesGroup

class ProfileStates(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()

class FoodStates(StatesGroup):
    waiting_for_product = State()
    waiting_for_grams = State()

class WaterStates(StatesGroup):
    waiting_for_amount = State()

class WorkoutStates(StatesGroup):
    waiting_for_type = State()
    waiting_for_minutes = State()