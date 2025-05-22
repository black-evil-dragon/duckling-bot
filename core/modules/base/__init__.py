from functools import wraps
from typing import Callable
from telegram import Update
from telegram.ext import Application, ContextTypes

from core.settings import COMMANDS



#* Telegram bot framework ________________________________________________________________________

#* Core ________________________________________________________________________

#* Other packages ________________________________________________________________________


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
    
    

    # * ____________________________________________________________
    # * |               Command handlers                            |
    # ...

    #? /some_command - some command
    def some_command(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE') -> None:
        return 
    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Message handlers                            |
    # ...
    # * |___________________________________________________________|


    # * ____________________________________________________________
    # * |               Callback handlers                            |
    # ...
    # * |___________________________________________________________|