
# * TEXT ___________________________________________________________________
choose_institute = "Пожалуйста, выберите институт из предложенных вариантов."
choose_course = "Пожалуйста, выберите курс из предложенных вариантов."
choose_group = "Пожалуйста, выберите группу из предложенных вариантов. Также вы можете ввести номер группы вручную.\n\nПример: рпс, рпс-21, рпс 21, 4б09"
choose_subgroup = "Пожалуйста, выберите подгруппу из предложенных вариантов."


institute_wrong_choice = "Не удалось определить институт."
course_wrong_choice = "Не удалось определить курс."
group_wrong_choice = "Не удалось определить группу."
subgroup_wrong_choice = "Не удалось определить подгруппу."


# * TEMPLATES ___________________________________________________________________
def result_subgroup_choice(subgroup):
    """
    TODO
    """
    return f"Подгруппа: {subgroup}"

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