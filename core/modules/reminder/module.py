
# * Telegram bot framework ________________________________________________________________________
import asyncio
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
    user_jobs = {}
    _instance: "ReminderModule" = None
    
    def __init__(self):
        self.user_jobs = {}
        self.__class__._instance = self
        self.user_jobs['1'] = 1

    def setup(self, application: "Application"):
        application.add_handler(CommandHandler(CommandNames.SHOW_REMINDER, self.show_reminder_info))
        application.add_handler(CommandHandler(CommandNames.SET_REMINDER, self.ask_reminder_time))
        
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_time_input),
            group=3
        )
        
        # application.create_task(self.restore_reminders(application))

        
        # job_queue = application.job_queue
        # job_queue.run_custom(
        #     name="reminder-getter",
        #     callback=self.get_subscribers_stack,
        #     job_kwargs=dict(
        #         trigger=IntervalTrigger(**dict(
        #             # **time,
        #             seconds=5,
        #             # day_of_week="mon-sat",
        #         ))
        #     )
        # )
        # job_queue.run_custom(
        #     name="reminder-sender",
        #     callback=self.schedule_broadcast,
        #     job_kwargs=dict(
        #         trigger=IntervalTrigger(**dict(
        #             # **time,
        #             seconds=10,
        #             # day_of_week="mon-sat",
        #         ))
        #     )
        # )
        
    # * ____________________________________________________________
    # * |               Helpers                                     |
    @classmethod
    def get_reminder_markup(cls, settings: dict):
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text=f"На сегодня {'✅' if settings.get('reminder_today', True) else '❌'}",
                    callback_data=f"settings#bool${not settings.get('reminder_today', True)}$reminder_today"
                ),
                InlineKeyboardButton(
                    text=f"На завтра {'✅' if not settings.get('reminder_today', True) else '❌'}",
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
        
        subscriber: "Subscriber" = Subscriber.objects.update_or_create(
            user_id=user.id,
            defaults=dict(
                schedule_time=time,
            )
        )
        
        await ReminderModule.sign_subscriber(subscriber, user_settings.get('reminder', False))
        
        
        # * Return
        await update.message.reply_text(
            text=messages.success_selected_time_template(time.strftime('%H:%M')),
            reply_markup=self.get_reminder_markup(user_settings)
        )
        return True
    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |                       Logic                               |
    @classmethod
    async def sign_subscriber(cls, subscriber: "Subscriber", is_sign: bool):
        if cls._instance is None:
            raise RuntimeError("ReminderModule not initialized")
        
        instance: 'ReminderModule' = cls._instance
        
        log.info(instance.user_jobs)
        
        if is_sign:
            # reminder_time = subscriber.schedule_time
            # await instance.set_reminder_for_user(
            #     subscriber, reminder_time, cls._instance.application
            # )
            pass
        else:
            # await instance.stop_reminder_for_user(
            #     user_id, cls._instance.application
            # )
            pass
        
        await asyncio.sleep(1)
        
    
    
    async def restore_reminders(self, application: "Application"):
        """Восстанавливаем напоминания из БД при старте бота"""
        await 1
        return
        reminders = Subscriber.get_active_subscribers()
        
        for user_id, reminder_time in reminders:
            await self.set_reminder_for_user(user_id, reminder_time, application)
            
    
    
    async def set_reminder_for_user(self, subscriber: Subscriber, reminder_time: datetime.time, application: "Application"):
        # Останавливаем предыдущее напоминание если есть
        user_id = subscriber.user_id
        user_data: dict = subscriber.user.get_user_data()
        await self.stop_reminder_for_user(subscriber.user_id, application)
        
        # Создаем уникальное имя задачи
        job_name = f"reminder_{subscriber.user_id}"
        
        # Добавляем задачу в планировщик
        job = application.job_queue.run_daily(
            callback=self.send_schedule_to_user,
            time=reminder_time,
            days=tuple(range(7)),
            data=dict(**user_data),
            name=job_name
        )
        
        # Сохраняем ссылку на задачу
        self.user_jobs[user_id] = job

    # * |___________________________________________________________|