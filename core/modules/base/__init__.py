# Вообще по хорошему тут все переделать, но так исторически сложилось


#* Telegram bot framework ________________________________________________________________________
from telegram import InlineKeyboardButton, Update
from telegram.ext import Application, ContextTypes


#* Core ________________________________________________________________________
from core.models.user import User
from core.modules.base.decorators import ensure_user_settings
from core.settings import COMMANDS


#* Other packages ________________________________________________________________________
from functools import wraps
from typing import Callable




class BaseMessages:
    # * TEXT ___________________________________________________________________

    help_text = '\n'.join((
        f'/{command} - {description}' for command, description in COMMANDS
    ))

    # * TEMPLATES ___________________________________________________________________




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
    # * |               Decorators and utils                         |
    @staticmethod
    def set_command_process(is_run: bool, context: 'ContextTypes.DEFAULT_TYPE'):
        context.user_data.update(dict(
            is_command_process=is_run
        ))
        return context
    

    @staticmethod
    def command_process(is_run: bool):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE', **kwargs):

                context = BaseModule.set_command_process(is_run, context)
                
                return await func(update, context, **kwargs)
            
            return wrapper
        return decorator
    
    @staticmethod
    @ensure_user_settings(need_update=True)
    async def update_user_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
        return
    
    
    # * Buttons
    menu_button = InlineKeyboardButton("📍 Меню", callback_data="delegate#menu")

    @staticmethod
    def delegate_button_template(text, command):
        return InlineKeyboardButton(text=text, callback_data=f"delegate#{command}")
    # * |___________________________________________________________|


    
    

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