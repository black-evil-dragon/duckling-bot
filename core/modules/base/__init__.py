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