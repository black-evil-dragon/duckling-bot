
# * TEXT ___________________________________________________________________
choose_institute = "Выберите институт:"
choose_course = "Выберите курс:"
choose_group = "Выберите группу:"



institute_wrong_choice = "Пожалуйста, выберите институт из предложенных вариантов."
course_wrong_choice = "Пожалуйста, выберите курс из предложенных вариантов."
group_wrong_choice = "Пожалуйста, выберите группу из предложенных вариантов."



# * TEMPLATES ___________________________________________________________________
def result_choices(institute, course, group):
    """
    TODO
    """
    return f"Институт: {institute}\nКурс: {course}\nГруппа: {group}"

def dialog_choose_course(institute_name: str) -> str:
    """
    TODO
    """
    return f"Выбран институт {institute_name}. Теперь выберите курс:"

def dialog_choose_group(course: str) -> str:
    """
    TODO
    """
    return f"Выбран курс {course}. Теперь выберите группу:"