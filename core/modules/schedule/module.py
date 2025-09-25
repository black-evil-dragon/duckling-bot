
#* Telegram bot framework ________________________________________________________________________
from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application

#* Core ________________________________________________________________________
from core.modules.base import BaseModule, strf_time_mask
from core.modules.base.decorators import ensure_user_settings
from core.modules.group.module import GroupModule

from core.session import Session
from core.settings.commands import CommandNames

from .formatters import prepare_schedule_weeks_data, prepare_schedule_day_data

from . import messages


#* Other packages ________________________________________________________________________
from datetime import datetime, timedelta
from datetime import date as DateType
from typing import Tuple
from utils.logger import get_logger


import traceback
import requests




log = get_logger()



#* Module ________________________________________________________________________
class ScheduleModule(BaseModule):
    class WeekDay:
        MONDAY = 0
        TUESDAY = 1
        WEDNESDAY = 2
        THURSDAY = 3
        FRIDAY = 4
        SATURDAY = 5
        SUNDAY = 6
    


    def setup(self, application: Application):
        # Command
        application.add_handler(CommandHandler(CommandNames.SCHEDULE, self.schedule_handler))
        application.add_handler(CommandHandler(CommandNames.WEEK, self.get_schedule_week))
        application.add_handler(CommandHandler(CommandNames.TODAY, self.get_schedule_day))
        application.add_handler(CommandHandler(CommandNames.TOMORROW, self.get_schedule_next_day))

        # Callback
        application.add_handler(CallbackQueryHandler(self.schedule_day_callback, pattern="^schedule_day#"))
        application.add_handler(CallbackQueryHandler(self.schedule_week_callback, pattern="^schedule_week#"))


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
        
        response_json: dict = response.json()
        
        if response_json.get('last_update'):
            response_json['last_update'] = datetime.strptime(response_json['last_update'], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M:%S")
            
        return response_json
    
    
    
    @staticmethod
    def get_schedule_query(
        group_id: int = None,
        user_data: dict = None,
        date_start: str = datetime.today().strftime(strf_time_mask),
        date_end: str = None,
        additional: dict = None
    ):  
        if user_data is None:
            user_data = {}

        user_settings: dict = user_data.get('user_settings', {})
        
        params = dict(
            group_id=str(user_data.get('selected_group', None) or group_id),
            selected_lesson_type="typical",
        )
         
       
        if date_end is not None:
            params.update(dict(
                date_start=date_start,
                date_end=date_end,
            ))
            
        else:
            params.update(dict(
                date=date_start,
            ))
        
        
        if user_settings.get('subgroup_lock', False) and user_data.get('selected_subgroup'):
            params.update(dict(
                subgroup=user_data.get('selected_subgroup')
            ))
            

        if additional is not None:
            params.update(**additional)
        

        return params
    
    
    
    @staticmethod
    def get_prev_next_day(current_day: 'DateType', strftime=False) -> Tuple[DateType, DateType] | Tuple[str, str]:
        """
        Возвращает кортеж дат +- день от текущего дня

        args:
            `current_day` (DateType): День, от которого идет отсчет

        returns:
            Tuple[date, date]: Кортеж дат
        """
        
        WeekDay = ScheduleModule.WeekDay
        

        if current_day.weekday() != WeekDay.MONDAY:
            prev_date = current_day - timedelta(days=1)
        else:
            prev_date = current_day - timedelta(days=2)

        
        if current_day.weekday() != WeekDay.SATURDAY:
            next_date = current_day + timedelta(days=1)
        else:
            next_date = current_day + timedelta(days=2)
        
        if strftime:
            prev_date = prev_date.strftime(strf_time_mask)
            next_date = next_date.strftime(strf_time_mask)

        return prev_date, next_date

    
    
    @classmethod
    def get_schedule_by_group_id(
        cls,
        session: 'requests.Session',
        group_id: int,
        date_start: "str" = datetime.today().strftime(strf_time_mask),
        date_end: "str" = None,
        additional: dict = None
    ) -> dict:
        data = dict(
            group_id=group_id,
            date_start=date_start,
            date_end=date_end,
        )
    
        if additional is not None:
            data.update(**additional)

        request = dict(
            session=session,
            path="schedule/day/",
            params=cls.get_schedule_query(**data),
        )
        
        response_data: dict = ScheduleModule.fetch_data(**request)

        return response_data
    
    
    @classmethod
    def get_message_schedule(cls, data: dict, is_daily: bool = True, date: "DateType" = datetime.today()) -> dict:
        formatter = None
        serializer = None
        
        
        if is_daily:
            formatter = prepare_schedule_day_data
            serializer = messages.format_schedule_day
        else:
            formatter = prepare_schedule_weeks_data
            serializer = messages.format_schedule_weeks
            

        prepare_data = formatter(data.get("data", {}))
        message = serializer(prepare_data)
        
        prev_key, next_key = cls.get_prev_next_day(date, strftime=True)
         
        callback_data = 'schedule_day' if is_daily else 'schedule_week'
        entity = 'День' if is_daily else 'Неделя'
        
        
        return dict(
            text=message,
            parse_mode='HTML',
            reply_markup=messages.use_paginator(
                callback_data=callback_data,
                entity=entity,
                prev_key=prev_key,
                next_key=next_key,

                additional_buttons=[messages.get_refresh_button(f'{callback_data}#{date.strftime(strf_time_mask)}')]
            )
        )
    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Command handlers                            |
    @staticmethod
    @ensure_user_settings()
    async def schedule_handler(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):

        schedule_week = context.user_data.get('user_settings', {}).get('show_week', True)

        if schedule_week:
            await ScheduleModule.get_schedule_week(update, context)
        else:
            await ScheduleModule.get_schedule_day(update, context)
            
            
            
    @staticmethod
    @ensure_user_settings()
    async def get_schedule_next_day(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        context.user_data['need_tomorrow'] = True

        await ScheduleModule.get_schedule_day(update, context)

    
    
    @staticmethod
    @ensure_user_settings()
    async def get_schedule_day(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')
    
        update_message = update.message or update.callback_query.message
    
        
        if not session:
            await update_message.reply_text(messages.session_error)
            return


        if not context.user_data.get('selected_group', False):
            await GroupModule.ask_institute(update, context)
            return


        
        try:
            today = datetime.now().date()
            
            if context.user_data.get('need_tomorrow', False):
                today += timedelta(days=1)
                context.user_data.update(dict(need_tomorrow=False))
                
            today_string = today.strftime(strf_time_mask)
    
    
            request = dict(
                session=session,
                path="schedule/day/",
                params=ScheduleModule.get_schedule_query(
                    user_data=context.user_data,
                    date_start=today_string,
                )
            )
            
            response_data: dict = ScheduleModule.fetch_data(**request)

            context.user_data['schedule_day_data'] = dict(
                **prepare_schedule_day_data(response_data.get("data", {})),
            )


            message = messages.format_schedule_day(context.user_data['schedule_day_data'])
            prev_key, next_key = ScheduleModule.get_prev_next_day(today, strftime=True) 


            await update_message.reply_text(
                text=message,
                parse_mode='HTML',
                reply_markup=messages.use_paginator(
                    callback_data='schedule_day',
                    entity='День',
                    prev_key=prev_key,
                    next_key=next_key,

                    additional_buttons=[messages.get_refresh_button(f'schedule_day#{today_string}')]
                )
            )
            
        except Exception:
            traceback.print_exc()
            await update_message.reply_text(messages.server_error)
        


    @staticmethod
    @ensure_user_settings()
    async def get_schedule_week(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')
    
        update_message = update.message or update.callback_query.message

        
        if not session:
            await update_message.reply_text(messages.session_error)
            return


        if not context.user_data.get('selected_group', False):
            await GroupModule.ask_institute(update, context)
            return

        
        try:
            # Получаем расписание группы для трех недель
            today = datetime.now().date()
        
            request = dict(
                session=session,
                path="schedule/weeks/",
                params=ScheduleModule.get_schedule_query(
                    user_data=context.user_data,
                    date_start=today.strftime(strf_time_mask),
                    date_end=(today + timedelta(weeks=3)).strftime(strf_time_mask),
                )
            )
            
            response_data: dict = ScheduleModule.fetch_data(**request)    


            schedule = dict(
                group=response_data.get("group", ""),
                data=prepare_schedule_weeks_data(response_data.get("data", {})),
            )
            context.user_data['schedule_weeks_data'] = schedule
            
            message = messages.format_schedule_weeks(schedule, 0)
            next_key = None if not len(schedule['data']) - 1 else 1

            await update_message.reply_text(
                text=message,
                parse_mode='HTML',
                reply_markup=messages.use_paginator(
                    callback_data='schedule_week',
                    entity='Неделя',

                    next_key=next_key,
                )
            )
            
            await update_message.reply_text(
                text=messages.schedule_warning_cache,
                parse_mode='HTML'
            )
            
        except Exception:
            traceback.print_exc()
            await update_message.reply_text(messages.server_error, parse_mode='HTML')

    # * |___________________________________________________________|




    # * ____________________________________________________________
    # * |               Callback handlers                            |
    async def schedule_week_callback(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        query = update.callback_query
        await query.answer()

        week_idx = int(query.data.split('#')[-1])
        

        data = context.user_data.get('schedule_weeks_data')
        if not data:
            await query.edit_message_text(messages.schedule_without_data)
            return
        
        message = messages.format_schedule_weeks(data, week_idx)
        
        prev_key = None if week_idx == 0 else week_idx - 1
        next_key = None if week_idx == len(data['data']) - 1 else week_idx + 1
        
        
        await query.edit_message_text(
            text=message,
            parse_mode='HTML',
            reply_markup=messages.use_paginator(
                callback_data='schedule_week',
                entity='Неделя',
                prev_key=prev_key,
                next_key=next_key,
                
            )
        )



    @staticmethod
    @ensure_user_settings()
    async def schedule_day_callback(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')
        
        query = update.callback_query
        query_data = query.data.split('#')
        query_date = datetime.strptime(query_data[-1], "%Y-%m-%d")
        
        await query.answer()


        if not session:
            await query.edit_message_text(messages.session_error)
            return

        query_date_string = query_date.strftime("%Y-%m-%d")
        request = dict(
            session=session,
            path="schedule/day/",
            params=ScheduleModule.get_schedule_query(
                user_data=context.user_data,
                date_start=query_date_string,
            )
        )
            
        response_data: dict = ScheduleModule.fetch_data(**request)
    
        
        if not response_data:
            await query.edit_message_text(messages.schedule_without_data)
            return
        

        context.user_data.update(dict(
            schedule_day_data=dict(
                **prepare_schedule_day_data(response_data.get("data", {})),
            )
        ))
        
        message = messages.format_schedule_day(context.user_data.get('schedule_day_data'))
        prev_key, next_key = ScheduleModule.get_prev_next_day(query_date, strftime=True)
        
        await query.edit_message_text(
            text=message,
            parse_mode='HTML',
            reply_markup=messages.use_paginator(
                callback_data='schedule_day',
                entity='День',
                prev_key=prev_key,
                next_key=next_key,

                additional_buttons=[messages.get_refresh_button(f'schedule_day#refresh#{query_date_string}')]
            )
        )
    # * |___________________________________________________________|