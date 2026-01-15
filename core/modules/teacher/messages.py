from telegram import KeyboardButton, ReplyKeyboardMarkup
from typing import Dict



choose_teacher_fio = (
    "Пожалуйста, выбирете преподавателя из продложенных вариантов. "
    "Также вы можете ввести ФИО преподавателя сразу."
    "\n\n"
    "Пример: Иванов Иван, Иванов, Иван"
)


empty_teachers = (
    "Не удалось найти преподавателя с таким ФИО, попробуйте еще раз."
)



# * REPLY MARKUPS

def result_choices(teacher: Dict[str, str]):
    return f"Выбран преподаватель: {teacher.get('degree')} {teacher.get('name')}"

def get_teachers_reply_markup(teachers):
    return ReplyKeyboardMarkup([
        [
            KeyboardButton(teacher.get('name'))
            for teacher in teachers[i:i+2]
        ] for i in range(0, len(teachers[:150]), 2)
    ], one_time_keyboard=True, resize_keyboard=True)