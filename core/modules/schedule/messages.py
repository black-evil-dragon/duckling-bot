
# * TEXT ___________________________________________________________________

schedule_wihtout_data = "Данные расписания устарели. Запросите расписание снова\n\n/schedule"


session_error = "Произошла ошибка при установке сессии\n\nПопробуйте снова позже"
server_error = "Произошла ошибка при запросе к серверу\n\nПопробуйте снова позже"



# * TEMPLATES ___________________________________________________________________
def schedule_title(title):
    return f"<b>📅 Расписание группы {title}</b>\n"


def week_info(week_type, first_date, last_date):
    return f"<b>| {week_type} | {first_date} - {last_date} |</b>\n\n"


def schedule_content(lesson):
    time = lesson[0]
    lesson_type = lesson[1]
    room = lesson[2]
    teacher = lesson[3]
    subject = lesson[4]
    subgroup = f" - ({lesson[5]})" if lesson[5] else ""
    
    return (
        f"* 🕒 <b>{time}{subgroup}</b>\n"
        f"| 📚 {subject}\n"
        f"| 🏷 Тип: {lesson_type}\n"
        f"| 👨‍🏫 {teacher}\n"
        f"| 📍 {room}\n\n"
    )
    