
#* Telegram bot framework ________________________________________________________________________
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application

#* Core ________________________________________________________________________
from core.modules.base import BaseModule
from core.session import Session

from core.modules.group.formatters import create_schedule_keyboard
from .formatters import format_schedule_week

from . import messages
from core.modules.group import messages as group_messages


from core.data.group import GROUP_IDS

#* Other packages ________________________________________________________________________
from datetime import datetime, timedelta
import json
import logging



log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)

#* Module ________________________________________________________________________
class ScheduleModule(BaseModule):
    
    

    def __init__(self):
        log.info("ScheduleModule initialized")


    def setup(self, application: Application):
        # Command
        application.add_handler(CommandHandler("schedule", self.get_schedule))

        # Callback
        application.add_handler(CallbackQueryHandler(self.schedule_callback, pattern="^week_"))


    



    # * ____________________________________________________________
    # * |               Command handlers                            |
    async def get_schedule(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')
        
        if not session:
            await update.message.reply_text("Ошибка: сессия не инициализирована")
            return

        # Если группа не выбрана, показываем клавиатуру с группами
        if 'group_id' not in context.user_data:
            buttons = [[KeyboardButton(institute)] for institute in GROUP_IDS.keys()]
            reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

            await update.message.reply_text(group_messages.choose_institute, reply_markup=reply_markup)

            return

        # Автоматический расчет дат (сегодня + 3 недели)
        today = datetime.now().date()
        date_start = today.strftime("%Y-%m-%d")
        date_end = (today + timedelta(weeks=3)).strftime("%Y-%m-%d")
        
        try:
            response = session.post(
                "https://tt2.vogu35.ru/",
                data=json.dumps({
                    "group_id": context.user_data['group_id'],
                    "date_start": date_start,
                    "date_end": date_end,
                    "selected_lesson_type": "typical",
                })
            )
            response.raise_for_status()
            data = response.json()
            

            context.user_data['schedule_data'] = data
            

            message = format_schedule_week(data, 0)

            total_weeks = len(data['schedule']) - 1
            reply_markup = create_schedule_keyboard(0, total_weeks)
            


            await update.message.reply_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await update.message.reply_text(f"Произошла ошибка: {str(e)}")

    # * |___________________________________________________________|





    # * ____________________________________________________________
    # * |               Callback handlers                            |
    async def schedule_callback(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        query = update.callback_query
        await query.answer()
        
        # Получаем номер недели из callback_data
        week_idx = int(query.data.split('_')[1])
        
        # Получаем сохраненные данные
        data = context.user_data.get('schedule_data')
        if not data:
            await query.edit_message_text(messages.schedule_wihtout_data)
            return
        
        # Форматируем запрошенную неделю
        message = format_schedule_week(data, week_idx)
        
        # Обновляем клавиатуру
        total_weeks = len(data['schedule']) - 1
        reply_markup = create_schedule_keyboard(week_idx, total_weeks)
        
        await query.edit_message_text(
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    # * |___________________________________________________________|