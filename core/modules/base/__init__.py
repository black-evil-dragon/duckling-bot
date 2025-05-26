# Вообще по хорошему тут все переделать, но так исторически сложилось


#* Telegram bot framework ________________________________________________________________________
from telegram import Update
from telegram.ext import Application, ContextTypes


#* Core ________________________________________________________________________
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
    # * |___________________________________________________________|


    
    

    # * ____________________________________________________________
    # * |               Command handlers                            |

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Message handlers                            |
    # ...
    # * |___________________________________________________________|


    # * ____________________________________________________________
    # * |               Callback handlers                            |
    # ...
    # * |___________________________________________________________|