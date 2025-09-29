# Вообще по хорошему тут все переделать, но так исторически сложилось


#* Telegram bot framework ________________________________________________________________________
from telegram import InlineKeyboardButton
from telegram.ext import Application


#* Core ________________________________________________________________________
from core.modules.base.decorators import ensure_user_settings
from core.settings import COMMANDS


#* Other packages ________________________________________________________________________
from core.settings.commands import CommandNames


strf_time_mask = "%Y-%m-%d"


# !DEPRECATED
class BaseMessages:
    # * TEXT ___________________________________________________________________

    help_text = '\n'.join((
        f'/{command} - {description}' for command, description in COMMANDS
    ))
    
    
    attempts_error_message = f"Максимальное количество попыток, похоже, что что-то пошло не так.\nПопробуйте еще раз или сообщите об этом разработчику\n\n/{CommandNames.HELP}"

    # * TEMPLATES ___________________________________________________________________
# !END DEPRECATED



# * MODULE ___________________________________________________________________
class BaseModule:

    def __init__(self) -> None:
        pass
    
    def __repr__(self):
        return f"<class {self.__class__.__name__}>"
    
    def __str__(self):
        return f"<{self.__class__.__name__}>"

    def setup(self, application: 'Application') -> None:
        raise Exception('Функция не переопределена')

    
    
    
    # * ____________________________________________________________
    # * |                       Utils                               |

    # ? Well
    @staticmethod
    @ensure_user_settings()
    async def update_user_settings(*args, **kwargs):
        pass
    
    # * |___________________________________________________________|
    
    
    
    # * ____________________________________________________________
    # * |                        UI                                 |
    # * | Buttons
    menu_button = InlineKeyboardButton("📍 Меню", callback_data="delegate#menu")

    @staticmethod
    def delegate_button_template(text, command):
        return InlineKeyboardButton(text=text, callback_data=f"delegate#{command}")
    # * |___________________________________________________________|


    # COMMENT TEMPLATES
    

    # * ____________________________________________________________
    # * |               Command handlers                            |

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Message handlers                            |
    
    # * |___________________________________________________________|


    # * ____________________________________________________________
    # * |               Callback handlers                            |
    # ...
    # * |___________________________________________________________|