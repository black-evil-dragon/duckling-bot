
#* Telegram bot framework ________________________________________________________________________
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardMarkup, KeyboardButton, Update
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

from core.modules.group.module import GroupModule
from core.modules.schedule.module import ScheduleModule
from core.modules.start import messages



log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)

#* Module ________________________________________________________________________
class StartModule(BaseModule):

    application: 'Application' = None


    def __init__(self) -> None:
        log.info("StartModule initialized")


    def setup(self, application: 'Application') -> None:
        application.add_handler(MessageHandler(
            filters.ALL, 
            self.load_user_settings
        ), group=-1)

        application.add_handler(MessageHandler(
            ~filters.COMMAND, 
            self.some_text
        ), group=-1) 

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(CommandHandler("menu", self.get_menu))

        application.add_handler(CallbackQueryHandler(self.handle_inline_commands, pattern="^delegate_"))


        self.application = application



    async def handle_inline_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.user_data.get('is_delegated', True):
            MENU_COMMANDS = self.get_menu_commands()

            query = update.callback_query
            await query.answer()

            # Получаем номер недели из callback_data
            command = str(query.data.split('_')[1])
            
            handler_map = {
                command: func for command, _, func in MENU_COMMANDS
            }
            
            if command in handler_map:
                context.user_data['is_delegated'] = True
                await query.edit_message_text(
                    text="Окей! Повторное открытие меню:\n\n***/menu***",
                    parse_mode='MARKDOWN',
                    reply_markup=None
                )
                await handler_map[command](update, context)
            

        
    async def show_command_keyboard(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE') -> None:
        buttons = context.bot_data['command_keyboard']
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        update_message = update.message or update.callback_query.message
    
        await update_message.reply_text(
            messages.show_command_keyboard,
            reply_markup=reply_markup
        
        )



    # * ____________________________________________________________
    # * |               Command handlers                            |
    async def start(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user = update.effective_user

        await update.message.reply_text(
            f'{messages.start_hello(user.username)}\n\n{BaseMessages.help_text}'
        )

        await self.show_command_keyboard(update, context)


    async def help(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        update_message = update.message or update.callback_query.message
        
        await update_message.reply_text(BaseMessages.help_text)
        await self.show_command_keyboard(update, context)


    def get_menu_commands(self):
        MENU_COMMANDS = [
            (None, None, None),
            ("help", "Помощь", self.help),
            (None, None, None),

            ("schedule", "Расписание", ScheduleModule.get_schedule),
            ("today", "На сегодня", ScheduleModule.get_schedule_day),
            ("tomorrow", "На завтра", ScheduleModule.get_schedule_day),

            ("set_group", "Установить группу", GroupModule.ask_institute),
            (None, None, None),
            ("set_subgroup", "Установить подгруппу", GroupModule.ask_subgroup),
            
            ("settings", "Настройки", None)
        ]

        return MENU_COMMANDS

    async def get_menu(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        MENU_COMMANDS = self.get_menu_commands()

        context.user_data.update({'is_delegated': False})

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=desc, callback_data=f"delegate_{cmd}") for cmd, desc, _ in MENU_COMMANDS[i:i+3] if cmd] 
            for i in range(0, len(MENU_COMMANDS), 3)
        ])
        
        await update.message.reply_text(
            "📋 Главное меню:",
            reply_markup=reply_markup
        )

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Message handlers                            |
    async def some_text(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        if not context.user_data.get('is_command_process', False):
            await self.show_command_keyboard(update, context)

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