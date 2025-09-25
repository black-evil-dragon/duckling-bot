
# * Telegram bot framework ________________________________________________________________________
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Update

from telegram.ext import ContextTypes, Application
from telegram.ext import CommandHandler, MessageHandler, JobQueue, Job
from telegram.ext import filters

# * Core ________________________________________________________________________
from core.models.subscriber import Subscriber
from core.models.user import User
from core.modules.base import BaseModule


# * Other packages ________________________________________________________________________
from core.modules.base.decorators import ensure_dialog_branch, ensure_user_settings, set_dialog_branch
from core.modules.reminder import messages

from core.modules.schedule.module import ScheduleModule
from core.settings.commands import CommandNames
from utils.logger import get_logger


from typing import Dict, Tuple
import pytz
import datetime
import asyncio
import requests

log = get_logger()



class ReminderModule(BaseModule):
    content_cache: Dict[Tuple["datetime.date", int], str] = {}
    cache_lock = asyncio.Lock()
    
    user_jobs: Dict[str, "Job"] = {}
    
    application: "Application" = None
    instance: "ReminderModule" = None
    
    
    session: "requests.Session" = None
    
    def __init__(self):
        self.user_jobs = {}
        self.__class__.instance = self

    def setup(self, application: "Application"):
        application.add_handler(CommandHandler(CommandNames.SHOW_REMINDER, self.show_reminder_info))
        application.add_handler(CommandHandler(CommandNames.SET_REMINDER, self.ask_reminder_time))
        
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_time_input),
            group=3
        )
        
        self.__class__.application = application
        self.session = application.bot_data.get('session')
        
        application.job_queue.run_once(self.restore_reminders, when=2)
        
    # * ____________________________________________________________
    # * |               Helpers                                     |
    def get_job_name(self, user_id: int):
        return f"reminder_{user_id}"
    
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
    
    # * | broadcast ________________________________________________|
    async def schedule_broadcast(self, context: "ContextTypes.DEFAULT_TYPE"):
        # {'user_id': 959259687, 'first_name': 'BlackEvilDragon', 'last_name': None, 'username': 'blackevil_dragon', 'selected_group': 233, 'selected_subgroup': 3, 'user_settings': {'reminder': True}, 'user_model': <User: Пользователь BlackEvilDragon>}
        
        user_data: dict = context.job.data
        user_id = user_data.get('user_id')
        selected_group = user_data.get('selected_group')
        current_date = datetime.datetime.now().date()
        
        await asyncio.sleep(0.1)
        


        
        
    async def get_cached_content(self, current_date: "datetime.date", group_id: int, user_data: dict) -> str:
        cache_key = (current_date, group_id)
        
        # Проверяем кеш
        async with self.cache_lock:
            if cache_key in self.content_cache:
                log.debug(f"Используем кешированный контент для группы {group_id} на {current_date}")
                return self.content_cache[cache_key]
        
        # Генерируем новый контент
        content = await self.generate_broadcast_content(current_date, group_id, user_data)
        
        # Сохраняем в кеш
        if content:
            async with self.cache_lock:
                self.content_cache[cache_key] = content
                log.debug(f"Сгенерирован и закеширован контент для группы {group_id} на {current_date}")
        
        return content
        
        

    async def generate_broadcast_content(self, current_date: "datetime.date", group_id: int, user_data: dict) -> str:   
        args = dict( 
            session=self.session,
            group_id=group_id,
            additional={}
        )
        
        if user_data.get('user_settings'):
            user_settings: dict = user_data.get('user_settings', {})
            

            if not user_settings.get('reminder_today', True):
                args.update(dict(
                    date=current_date + datetime.timedelta(days=1),
                ))

            args["additional"].update(dict(
                user_settings=user_settings
            ))
        
        
        response: dict = ScheduleModule.get_schedule_by_group_id(**args)
        
        message = ScheduleModule.get_message_schedule(response, is_daily=True)
        
        print(message)
        await asyncio.sleep(0.1)
    

    # * | sign_subscriber __________________________________________|
    # ? | Подписываем пользователя на интервальное событие
    # ? | или отписываем
    @classmethod
    async def sign_subscriber(cls, subscriber: "Subscriber", is_sign: bool, user: "User" = None):
        if cls.instance is None:
            raise RuntimeError("ReminderModule not initialized")
        
        instance: 'ReminderModule' = cls.instance
        reminder_time = subscriber.schedule_time
        
        if not is_sign:
            await instance.stop_reminder_for_user(subscriber)   
            return

        if not reminder_time:
            await cls.ask_reminder_time()
            return
        
        await instance.set_reminder_for_user(subscriber, reminder_time, user)
        

    

    
    # * | Set reminder _____________________________________________|
    # ? | Ставим джобу
    async def set_reminder_for_user(self, subscriber: "Subscriber", reminder_time: "datetime.time", user: "User" = None):
        user: "User" = subscriber.get_user() if user is None else user

        user_id = user.id
        user_data: dict = user.get_user_data()
        
        # Останавливаем предыдущее напоминание, если есть
        await self.stop_reminder_for_user(subscriber)
        
        msk_tz = pytz.timezone('Europe/Moscow')
        utc_tz = pytz.timezone('UTC')
        now_msk = datetime.datetime.now(msk_tz)
        
        msk_datetime  = msk_tz.localize(datetime.datetime.combine(now_msk.date(), reminder_time))
        utc_datetime = msk_datetime.astimezone(utc_tz)
    
        job = self.application.job_queue.run_daily(
            callback=self.schedule_broadcast,
            time=utc_datetime,
            days=tuple(range(7)),
            data=dict(**user_data),
            name=self.get_job_name(user_id)
        )
        
        # Сохраняем ссылку на задачу
        self.user_jobs[user_id] = job
        
        log.debug(f'Установили напоминание для {user_id} {job}')
        
    
    # * | Set reminder _____________________________________________|
    # ? | Останавливаем джобу
    async def stop_reminder_for_user(self, subscriber: "Subscriber"):  
        user_id = subscriber.user_id
  
        jobs = self.application.job_queue.get_jobs_by_name(self.get_job_name(user_id))
        for job in jobs:
            job.schedule_removal()
            log.debug(f'Останавливаем напоминание для {user_id} {job}')
            
            
    # * | restore_reminders ________________________________________|
    # ? | Восстанавливаем все напоминания
    async def restore_reminders(self, context: "ContextTypes.DEFAULT_TYPE"):
        subscribers = Subscriber.get_active_subscribers()
        log.debug(f'Восстанавливаем напоминания {subscribers}')

        for subscriber in subscribers:
            log.debug(f'Возвращаем напоминание для {subscriber.user_id}')
            await self.set_reminder_for_user(subscriber, subscriber.schedule_time)
            

    # * |___________________________________________________________|