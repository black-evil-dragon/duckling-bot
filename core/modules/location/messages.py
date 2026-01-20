from typing import Dict
from telegram import KeyboardButton, ReplyKeyboardMarkup


empty_buildings = (
    "Не удалось найти корпус. Попробуйте еще раз."
)

empty_audiences = (
    "Не удалось найти кабинет. Попробуйте еще раз."
)


choose_audience = "Пожалуйста, введите номер кабинета:"
choose_building = "Пожалуйста, введите номер корпуса:"


def result_choices(location: Dict[str, str]):
    return f"Выбран: {location.get('address')}"

def get_locations_reply_markup(locations):
    return ReplyKeyboardMarkup([
        [
            KeyboardButton(teacher.get('address'))
            for teacher in locations[i:i+2]
        ] for i in range(0, len(locations[:150]), 2)
    ], one_time_keyboard=True, resize_keyboard=True)