
#* Telegram bot framework ________________________________________________________________________
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application

#* Core ________________________________________________________________________
from core.modules.base import BaseModule
from core.modules.group.module import GroupModule
from core.session import Session

from .formatters import prepare_schedule_weeks_data, prepare_schedule_day_data

from . import messages


#* Other packages ________________________________________________________________________
from datetime import datetime, timedelta
import logging
import traceback



log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)

#* Module ________________________________________________________________________
class ScheduleModule(BaseModule):
    
    

    def __init__(self):
        log.info("ScheduleModule initialized")


    def setup(self, application: Application):
        # Command
        application.add_handler(CommandHandler("schedule", self.get_schedule))
        application.add_handler(CommandHandler("today", self.get_schedule_day))


        # Callback
        application.add_handler(CallbackQueryHandler(self.schedule_callback, pattern="^week_"))



    
    # * ____________________________________________________________
    # * |               Command handlers                            |
    @staticmethod
    async def get_schedule_day(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE', today = datetime.now().date()):
        update_message = update.message or update.callback_query.message
        session: 'Session' = context.bot_data.get('session')
        
        if not session:
            await update_message.reply_text(messages.session_error)
            return


        if 'selected_group' not in context.user_data:
            await GroupModule.ask_institute(update, context)
            return

        
        
        try:
            # Получаем расписание группы для трех недель
            response = session.post(
                "schedule/day/",
                json={
                    "group_id": str(context.user_data['selected_group']),
                    "date": today.strftime("%Y-%m-%d"),
                    "selected_lesson_type": "typical",
                }
            )
            response.raise_for_status()
            response_data: dict = response.json()

            schedule = dict(
                **prepare_schedule_day_data(response_data.get("data", {})),
                last_update=response_data.get("last_update", ""),
            )
            context.user_data['schedule_day_data'] = schedule

            message = messages.format_schedule_day(schedule)
            reply_markup = messages.create_pagination_keyboard(0, 1, 'день')


            await update_message.reply_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
        except Exception:
            traceback.print_exc()
            await update_message.reply_text(messages.server_error)
        


    @staticmethod
    async def get_schedule(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        update_message = update.message or update.callback_query.message
        session: 'Session' = context.bot_data.get('session')
        
        
        if not session:
            await update_message.reply_text(messages.session_error)
            return


        if 'selected_group' not in context.user_data:
            await GroupModule.ask_institute(update, context)
            return

        # Автоматический расчет дат (сегодня + 3 недели)
        today = datetime.now().date()
        date_start = today.strftime("%Y-%m-%d")
        date_end = (today + timedelta(weeks=3)).strftime("%Y-%m-%d")
        
        try:
            # Получаем расписание группы для трех недель
            response = session.post(
                "schedule/",
                json={
                    "group_id": str(context.user_data['selected_group']),
                    "date_start": date_start,
                    "date_end": date_end,
                    "selected_lesson_type": "typical",
                }
            )
            response.raise_for_status()
            response_data: dict = response.json()

            schedule = dict(
                group=response_data.get("group", ""),
                data=prepare_schedule_weeks_data(response_data.get("data", {})),
                last_update=response_data.get("last_update", ""),
            )
            context.user_data['schedule_weeks_data'] = schedule
            

            message = messages.format_schedule_weeks(schedule, 0)

            total_weeks = len(schedule) - 1
            # reply_markup = messages.create_pagination_keyboard(0, total_weeks, 'неделя')


            await update_message.reply_text(
                message,
                parse_mode='HTML',
                # reply_markup=reply_markup
            )
            
        except Exception:
            print(response_data.get('error'))
            traceback.print_exc()
            await update_message.reply_text(messages.server_error)

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Message handlers                            |


    # * |___________________________________________________________|


    # * ____________________________________________________________
    # * |               Callback handlers                            |
    async def schedule_callback(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        query = update.callback_query
        await query.answer()
        
        # Получаем номер недели из callback_data
        week_idx = int(query.data.split('_')[1])
        
        # Получаем сохраненные данные
        data = context.user_data.get('schedule_weeks_data')
        if not data:
            await query.edit_message_text(messages.schedule_wihtout_data)
            return
        
        # Форматируем запрошенную неделю
        message = messages.format_schedule_weeks(data, week_idx)
        
        # Обновляем клавиатуру
        total_weeks = len(data['data']) - 1
        reply_markup = messages.create_pagination_keyboard(week_idx, total_weeks, 'неделя')
        
        await query.edit_message_text(
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    # * |___________________________________________________________|