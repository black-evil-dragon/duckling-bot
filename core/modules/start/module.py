
#* Telegram bot framework ________________________________________________________________________
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, Application
from telegram.ext import filters

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
        application.add_handler(MessageHandler(
            filters.ALL, 
            self.load_user_settings
        ), group=-1) 

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))

        

        
    

    # * ____________________________________________________________
    # * |               Command handlers                            |
    async def start(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user = update.effective_user

        await update.message.reply_text(
            f'{messages.start_hello(user.username)}\n\n{BaseMessages.help_text}'
        )


    async def help(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        await update.message.reply_text(BaseMessages.help_text)

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Message handlers                            |
    async def load_user_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.user_data.get('is_user_loaded', False): return
    
        if context.bot_data.get('db'):
            db: 'Database' = context.bot_data.get('db')
            user = update.effective_user
        
            user_data = {
                "id": user.id,
                "is_bot": user.is_bot,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
            }

            saved_data = db.get_user(user.id)
            if saved_data:
                user_data.update(dict(
                    selected_group=saved_data.get('group_id'),
                    selected_subgroup=saved_data.get('subgroup_id'),
                    is_user_loaded=True,
                ))

            db.add_or_update_user(user_data)
            context.user_data.update({**user_data})


    # * |___________________________________________________________|


    # * ____________________________________________________________
    # * |               Callback handlers                           |
    # ...
    # * |___________________________________________________________|