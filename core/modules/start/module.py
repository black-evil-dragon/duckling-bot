
#* Telegram bot framework ________________________________________________________________________
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application

#* Core ________________________________________________________________________
from core.modules.base import BaseMessages, BaseModule
from core.db import Database



from core.data.group import GROUP_IDS

#* Other packages ________________________________________________________________________
from datetime import datetime, timedelta
import json
import logging

from core.modules.start import messages



log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)

#* Module ________________________________________________________________________
class StartModule(BaseModule):
    def __init__(self) -> None:
        log.info("StartModule initialized")

    def setup(self, application: 'Application') -> None:
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))
    

    # * ____________________________________________________________
    # * |               Command handlers                            |
    async def start(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        db: 'Database' = context.bot_data.get('db')

        user = update.effective_user
        
        user_data = {
            "id": user.id,
            "is_bot": user.is_bot,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
        }
        

        if db.add_or_update_user(user_data):
            await update.message.reply_text(
                f'{messages.start_hello(user.username)}\n\n{BaseMessages.help_text}'
            )
        else:
            await update.message.reply_text(messages.start_error_register)



    async def help(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        await update.message.reply_text(BaseMessages.help_text)

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Message handlers                            |
    # ...
    # * |___________________________________________________________|


    # * ____________________________________________________________
    # * |               Callback handlers                           |
    # ...
    # * |___________________________________________________________|