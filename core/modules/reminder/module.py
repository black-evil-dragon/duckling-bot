
# * Telegram bot framework ________________________________________________________________________
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Update

from telegram.ext import ContextTypes, Application
from telegram.ext import CommandHandler, MessageHandler, JobQueue
from telegram.ext import filters

# * Core ________________________________________________________________________
from core.models.subscriber import Subscriber
from core.models.user import User
from core.modules.base import BaseModule


# * Other packages ________________________________________________________________________
from core.modules.base.decorators import ensure_dialog_branch, ensure_user_settings, set_dialog_branch
from core.modules.reminder import messages

from core.settings.commands import CommandNames
from utils.logger import get_logger


from typing import List, Set
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

import requests
import datetime

log = get_logger()



class ReminderModule(BaseModule):
    jobs = {}
    

    def setup(self, application: "Application"):
        application.add_handler(CommandHandler(CommandNames.SHOW_REMINDER, self.show_reminder_info))
        application.add_handler(CommandHandler(CommandNames.SET_REMINDER, self.ask_reminder_time))
        
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_time_input),
            group=3
        )

        
        # job_queue = application.job_queue
        # job_queue.run_custom(
        #     name="schedule-reminder-broadcast",
        #     callback=self.schedule_broadcast,
        #     job_kwargs=dict(
        #         trigger=IntervalTrigger(**dict(
        #             # **time,
        #             seconds=5,
        #             # day_of_week="mon-sat",
        #         ))
        #     )
        # )
        self.start_hybrid_scheduler(application)
        
        
    # * ____________________________________________________________
    # * |               Helpers                                     |
    @classmethod
    def get_reminder_markup(cls, settings: dict):
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=f"Расписание на сегодня {'✅' if settings.get('reminder_today', True) else '❌'}",
                    callback_data=f"settings#bool${not settings.get('reminder_today', True)}$reminder_today"
                ),
                InlineKeyboardButton(
                    text=f"Расписание на завтра {'✅' if not settings.get('reminder_today', True) else '❌'}",
                    callback_data=f"settings#bool${not settings.get('reminder_today', True)}$reminder_today"
                ), 
            ],
            [
                cls.delegate_button_template(
                    messages.choose_reminder_time_button,
                    f"{CommandNames.SET_REMINDER}"
                )
            ],
            [
                cls.menu_button, cls.delegate_button_template(
                    "Настройки",
                    f"{CommandNames.SETTINGS}"
                )
            ]
            ])
            

    # * ____________________________________________________________
    # * |               Command handlers                            |
    @classmethod
    @ensure_user_settings()
    async def show_reminder_info(cls, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        update_message = update.message or update.callback_query.message
        
        user: User = context.user_data.get('user_model')
        user_settings = user.get_user_settings()
        subscriber: Subscriber = Subscriber.objects.get_or_create(
            user_id=user.id,
        )
        
        user_time = subscriber.get_schedule_time(to_str=True)

        
        # * Пользовательский набор настроек
        text = messages.user_scheduled_reminder_template(time=user_time)
    
            
        # | Передача в контекст
        context.user_data.update(dict(
            send_custom_settings=True,
            get_custom_markup=cls.get_reminder_markup,
            custom_settings_text=text,
        ))
        
        
        await update_message.reply_text(
            text=text,
            reply_markup=cls.get_reminder_markup(user_settings)
        )
        

    @classmethod
    @ensure_user_settings()
    @set_dialog_branch('reminder_time')
    async def ask_reminder_time(cls, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        update_message = update.message or update.callback_query.message

        # * Return
        await update_message.reply_text(
            text=messages.ask_reminder_time,
        )
    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Callback handlers                           |
    @ensure_dialog_branch('reminder_time', stop_after=True)
    async def handle_time_input(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        user_input = update.message.text.strip()
        

        try:
            time = datetime.datetime.strptime(user_input, '%H:%M').time()
        except Exception:
            log.debug('Неверный формат времени', exc_info=True)
            await update.message.reply_text(messages.wrong_format_time)
            return False


        user: User = context.user_data.get('user_model')
        user_settings = user.get_user_settings()
        
        Subscriber.objects.update_or_create(
            user_id=user.id,
            defaults=dict(
                schedule_time=time,
            )
        )
        
        
        # * Return
        await update.message.reply_text(
            text=messages.success_selected_time_template(time.strftime('%H:%M')),
            reply_markup=self.get_reminder_markup(user_settings)
        )
        return True
    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |                       Logic                               |
    async def schedule_broadcast(self, context: "ContextTypes.DEFAULT_TYPE"):
        session: 'requests.Session' = context.bot_data.get('session')
        if not session: return
        
        
        
    
        
        
    @classmethod
    def start_hybrid_scheduler(cls, application: "Application"):
        """Гибридный подход: проверка каждые 5 минут + точное время"""
        job_queue = application.job_queue
        
        # Базовая проверка каждые 5 минут (для надежности)
        job_queue.run_repeating(
            callback=cls.schedule_broadcast,
            interval=300,  # 5 минут
            name="schedule-broadcast-5min"
        )
        
        # Точные проверки по расписанию
        cls.schedule_precise_checks(job_queue)
    
    @classmethod
    def schedule_precise_checks(cls, job_queue: "JobQueue"):
        """Планирует точные проверки по времени подписчиков"""
        unique_times: List['Subscriber'] = Subscriber.get_subscriber_by_unique_times()
        
        for subscriber in unique_times:
            if subscriber.schedule_time:
                cls.create_daily_job(job_queue, subscriber.schedule_time)
    
    @classmethod
    def create_daily_job(cls, job_queue: "JobQueue", schedule_time: datetime.time):
        """Создает ежедневную job на определенное время"""
        now = datetime.datetime.now()
        target_datetime = datetime.datetime.combine(now.date(), schedule_time)


        if target_datetime <= now:
            target_datetime += datetime.timedelta(days=1)
        

        job_queue.run_daily(
            callback=cls.schedule_broadcast,
            time=schedule_time,
            name=f"daily-schedule-{schedule_time.strftime('%H-%M')}",
            days=tuple(range(7))
        )
        

    # * |___________________________________________________________|