from core.settings.commands import COMMANDS, CommandNames


# * TEXT _______________________________________________
unknown_error = (
    "Непредвиденная ошибка. Попробуйте еще раз или сообщите об этом разработчику\n\n"
    f"/{CommandNames.START} - начало\n"
    f"/{CommandNames.HELP} - помощь\n"
    f"/{CommandNames.MENU} - меню"
)

attempts_error_message = (
    "Максимальное количество попыток, похоже, что что-то пошло не так.\n"
    "Попробуйте еще раз или сообщите об этом разработчику\n\n"
    f"/{CommandNames.START} - начало\n"
    f"/{CommandNames.HELP} - помощь\n"
    f"/{CommandNames.MENU} - меню\n"
)



start_text = (
    "Приветствуем вас в информационном сервисе ВоГУ! 📚\n\n"
    "Данный бот предоставляет доступ к расписанию университета. Мы стремимся сделать процесс получения информации максимально простым и удобным.\n\n"
    "• <b>Работает без перерывов и выходных</b>\n"
    "• <b>Обратная связь:</b> для сообщения о проблемах свяжитесь с разработчиком (контакты в GitHub).\n"
    "• <b>Развитие проекта:</b> мы приветствуем вашу помощь и идеи. Исходный код проекта доступны в репозитории:\n"
    "https://github.com/black-evil-dragon/duckling-bot\n\n"
    f"Чтобы увидеть список команд, введите: /{CommandNames.HELP}"
)




# * TEMPLATES ___________________________________________
def get_commands_text(commands: list[str] = COMMANDS):
    return '\n'.join((
        f'/{command} - {description}' for command, description in commands
    ))


calendar_chosen_text = lambda date : f"Выбрана дата {date}"  # noqa: E731
