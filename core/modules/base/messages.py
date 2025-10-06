from core.settings.commands import COMMANDS, CommandNames


# * TEXT _______________________________________________
unknown_error = (
    "Непредвиденная ошибка. Попробуйте еще раз или сообщите об этом разработчику\n\n"
    f"/{CommandNames.START} - начало\n"
    f"/{CommandNames.HELP} - помощь\n"
    f"/{CommandNames.MENU} - меню\n"
)

attempts_error_message = (
    "Максимальное количество попыток, похоже, что что-то пошло не так.\n"
    "Попробуйте еще раз или сообщите об этом разработчику\n\n"
    f"/{CommandNames.START} - начало\n"
    f"/{CommandNames.HELP} - помощь\n"
    f"/{CommandNames.MENU} - меню\n"
)



start_text = (
    "Кря-кря! 🐥 Привет! Я Утёнок, бот, который высидел для тебя расписание ВоГУ.\n\n"
    "Работаю без выходных, но если вдруг начну крякать невпопад — позови моего создателя. Ссылки на него в профиле создателя репозитория.\n\n"
    "Я скромный утёнок с большими амбициями! Ты можешь помочь мне вырасти в прекрасного лебедя? 🦢 Загляни в мой код и предложи свои идеи: \nhttps://github.com/black-evil-dragon/duckling-bot"
    f"\n\nМои команды: /{CommandNames.HELP}"
)



# * TEMPLATES ___________________________________________
def get_commands_text(commands: list[str] = COMMANDS):
    return '\n'.join((
        f'/{command} - {description}' for command, description in commands
    ))