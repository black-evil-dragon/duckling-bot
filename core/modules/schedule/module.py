
#* Telegram bot framework ________________________________________________________________________
from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application

#* Core ________________________________________________________________________
from core.db import Database
from core.modules.base import BaseModule
from core.modules.base.decorators import ensure_user_settings
from core.modules.group.module import GroupModule
from core.session import Session

from .formatters import prepare_schedule_weeks_data, prepare_schedule_day_data

from . import messages


#* Other packages ________________________________________________________________________
from datetime import datetime, timedelta
import logging
import traceback
import requests


log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)

#* Module ________________________________________________________________________
class ScheduleModule(BaseModule):
    
    

    def __init__(self):
        log.info("ScheduleModule initialized")


    def setup(self, application: Application):
        # Command
        application.add_handler(CommandHandler("schedule", self.schedule_handler))
        application.add_handler(CommandHandler("week", self.get_schedule_week))
        application.add_handler(CommandHandler("today", self.get_schedule_day))
        application.add_handler(CommandHandler("tomorrow", self.get_schedule_next_day))

        # Callback
        application.add_handler(CallbackQueryHandler(self.schedule_day_callback, pattern="^schedule_day_"))
        application.add_handler(CallbackQueryHandler(self.schedule_week_callback, pattern="^schedule_week_"))


    # * ____________________________________________________________
    # * |                    Utils                                  |
    @classmethod
    def fetch_data(
        cls,
        session: 'requests.Session',
        path: str,
        params: dict,
    ) -> dict:
        response = session.post(
            path,
            json=params
        )

        response.raise_for_status()
        return response.json()
    

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Command handlers                            |
    @staticmethod
    @ensure_user_settings(need_update=True)
    async def schedule_handler(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):

        schedule_week = context.user_data.get('user_settings', {}).get('show_week', True)

        if schedule_week:
            await ScheduleModule.get_schedule_week(update, context)
        else:
            await ScheduleModule.get_schedule_day(update, context)
            
            
    @staticmethod
    async def get_schedule_next_day(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        context.user_data['need_tomorrow'] = True

        await ScheduleModule.get_schedule_day(update, context)



    @staticmethod
    @ensure_user_settings(need_update=True)
    async def get_schedule_day(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')
        db: 'Database' = context.bot_data.get('db')
    
        update_message = update.message or update.callback_query.message
        user = update.effective_user
        user_settings = {}

        if db is not None:
            user_settings = db.get_user(user.id).get('user_settings', {})
        
        if not session:
            await update_message.reply_text(messages.session_error)
            return


        if not context.user_data.get('selected_group', False):
            await GroupModule.ask_institute(update, context)
            return


        
        try:
            today = datetime.now().date()
            
            prev_date = today - timedelta(days=1) if today.weekday() != 0 else today - timedelta(days=2)
            next_date = today + timedelta(days=1) if today.weekday() != 5 else today + timedelta(days=2)
            

            if context.user_data.get('need_tomorrow', False) or today.weekday() == 6:
                today = next_date
                prev_date = today - timedelta(days=1) if today.weekday() != 0 else today - timedelta(days=2)
                next_date = today + timedelta(days=1) if today.weekday() != 5 else today + timedelta(days=2)
                
                context.user_data.update(dict(need_tomorrow=False))
            

            params = {
                "group_id": str(context.user_data['selected_group']),
                "date": today.strftime("%Y-%m-%d"),
                "selected_lesson_type": "typical",
            }

            if user_settings.get('subgroup_lock', False) and context.user_data.get('selected_subgroup'):
                params.update({
                    'subgroup': context.user_data['selected_subgroup']
                })


            response_data: dict = ScheduleModule.fetch_data(session, "schedule/day/", params)

            if response_data.get('last_update'):
                response_data['last_update'] = datetime.strptime(response_data['last_update'], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M:%S")


            schedule = dict(
                **prepare_schedule_day_data(response_data.get("data", {})),
                last_update=response_data.get("last_update", ""),
            )
            context.user_data['schedule_day_data'] = schedule


            message = messages.format_schedule_day(schedule)

            prev_key = prev_date.strftime("%Y-%m-%d")
            next_key = next_date.strftime("%Y-%m-%d")

            reply_markup = messages.use_paginator('schedule_day', prev_key, next_key, 'День')


            await update_message.reply_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
        except Exception:
            traceback.print_exc()
            await update_message.reply_text(messages.server_error)
        


    @staticmethod
    async def get_schedule_week(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')
        db: 'Database' = context.bot_data.get('db')
    
        update_message = update.message or update.callback_query.message
        user = update.effective_user
        user_settings = {}

        if db is not None:
            user_settings = db.get_user(user.id).get('user_settings', {})
        
        
        if not session:
            await update_message.reply_text(messages.session_error)
            return


        if not context.user_data.get('selected_group', False):
            await GroupModule.ask_institute(update, context)
            return


        today = datetime.now().date()
        date_start = today.strftime("%Y-%m-%d")
        date_end = (today + timedelta(weeks=3)).strftime("%Y-%m-%d")
        
        try:
            # Получаем расписание группы для трех недель
            params = {
                "group_id": str(context.user_data['selected_group']),
                "date_start": date_start,
                "date_end": date_end,
                "selected_lesson_type": "typical",
            }
            if user_settings.get('subgroup_lock', False) and context.user_data.get('selected_subgroup'):
                params.update({
                    'subgroup': context.user_data['selected_subgroup']
                })
            response_data = ScheduleModule.fetch_data(session, "schedule/", params)

            schedule = dict(
                group=response_data.get("group", ""),
                data=prepare_schedule_weeks_data(response_data.get("data", {})),
                last_update=response_data.get("last_update", ""),
            )
            context.user_data['schedule_weeks_data'] = schedule
            

            next_key = None if not len(schedule['data']) - 1 else 1

            await update_message.reply_text(
                text=messages.format_schedule_weeks(schedule, 0),
                parse_mode='HTML',
                reply_markup=messages.use_paginator(
                    callback_data='schedule_week',
                    next_key=next_key,
                    entity='Неделя'
                )
            )
            
        except Exception:
            traceback.print_exc()
            await update_message.reply_text(messages.server_error, parse_mode='HTML')

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Message handlers                            |


    # * |___________________________________________________________|


    # * ____________________________________________________________
    # * |               Callback handlers                            |
    async def schedule_week_callback(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        query = update.callback_query
        await query.answer()

        week_idx = int(query.data.split('_')[-1])
        

        data = context.user_data.get('schedule_weeks_data')
        if not data:
            await query.edit_message_text(messages.schedule_wihtout_data)
            return
        

        prev_key = None if week_idx == 0 else week_idx - 1
        next_key = None if week_idx == len(data['data']) - 1 else week_idx + 1
        
        await query.edit_message_text(
            text=messages.format_schedule_weeks(data, week_idx),
            parse_mode='HTML',
            reply_markup=messages.use_paginator(
                callback_data='schedule_week',
                prev_key=prev_key,
                next_key=next_key, 
                entity='Неделя'
            )
        )



    @staticmethod
    @ensure_user_settings()
    async def schedule_day_callback(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')
        db: 'Database' = context.bot_data.get('db')

        query = update.callback_query
        user = update.effective_user

        user_settings = {}

        if db is not None:
            user_settings = db.get_user(user.id).get('user_settings', {})
        
        await query.answer()

        if not session:
            await query.edit_message_text(messages.session_error)
            return
        

        query_date = datetime.strptime(query.data.split('_')[-1], "%Y-%m-%d")

        prev_date = query_date - timedelta(days=1) if query_date.weekday() != 0 else query_date - timedelta(days=2)
        next_date = query_date + timedelta(days=1) if query_date.weekday() != 5 else query_date + timedelta(days=2)

        prev_key = prev_date.strftime("%Y-%m-%d")
        next_key = next_date.strftime("%Y-%m-%d")

        
        params = {
            "group_id": str(context.user_data['selected_group']),
            "date": query_date.strftime("%Y-%m-%d"),
            "selected_lesson_type": "typical",
        }

        if user_settings.get('subgroup_lock', False) and context.user_data.get('selected_subgroup'):
            params.update({
                'subgroup': str(context.user_data['selected_subgroup'])
            })

        
        response_data: dict = ScheduleModule.fetch_data(
            session,
            "schedule/day/",
            params
        )
        if not response_data:
            await query.edit_message_text(messages.schedule_wihtout_data)
            return
        
        if response_data.get('last_update'):
            response_data['last_update'] = datetime.strptime(response_data['last_update'], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M:%S")
        schedule = dict(
            **prepare_schedule_day_data(response_data.get("data", {})),
            last_update=response_data.get("last_update", ""),
        )
        context.user_data['schedule_day_data'] = schedule
        
        

        message = messages.format_schedule_day(schedule)
        reply_markup = messages.use_paginator('schedule_day', prev_key, next_key, 'День')
        
        await query.edit_message_text(
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    # * |___________________________________________________________|