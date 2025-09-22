# * Telegram bot framework ________________________________________________________________________
from typing import List
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application

# * Core ________________________________________________________________________
from core.models.subscriber import Subscriber
from core.models.user import User
from core.modules.base import BaseModule


# * Other packages ________________________________________________________________________
from core.modules.base.decorators import ensure_user_settings
from core.modules.reminder import messages
from core.modules.schedule.module import ScheduleModule
from core.settings.commands import CommandNames

from db.core import Database
from utils.logger import get_logger

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger


log = get_logger()


class ReminderModule(BaseModule):
    jobs = {}
    
    

    def setup(self, application: "Application"):
        application.add_handler(CommandHandler(CommandNames.SHOW_REMINDER, self.show_reminder_info))
        application.add_handler(CommandHandler(CommandNames.SET_REMINDER, self.ask_reminder_time))
        
        application.add_handler(CallbackQueryHandler(self.set_reminder_time, pattern="^set_reminder_time#"))

        
        job_queue = application.job_queue
        for task_name, time in Subscriber.cron_data.items():
            job_queue.run_custom(
                name=task_name,
                callback=self.schedule_broadcast,
                job_kwargs=dict(
                    trigger=IntervalTrigger(**dict(
                        # **time,
                        seconds=5,
                        # day_of_week="mon-sat",
                    ))
                )
            )

    # * ____________________________________________________________
    # * |               Command handlers                            |
    @classmethod
    @ensure_user_settings()
    async def show_reminder_info(cls, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        update_message = update.message or update.callback_query.message
        _, time_label = context.user_data.get("scheduled_time")

        message = messages.user_scheduled_reminder_template(time_label)

        await update_message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup([[cls.delegate_button_template(messages.choose_reminder_time_button, f"delegate#{CommandNames.SET_REMINDER}")]])
        )
        
        



    @classmethod
    @ensure_user_settings()
    async def ask_reminder_time(cls, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        update_message = update.message or update.callback_query.message
        # choices = Subscriber.TimeChoices.choices()
        # user_settings: dict = context.user_data.get('user_settings', {})
        
    
        # def get_actual_markup(user_settings: dict):
        #     keyboard = []
        #     count_in_row = 2
    
        #     for i in range(0, len(choices), count_in_row):
        #         row = []

        #         if i == 0:
        #             keyboard += [[InlineKeyboardButton(
        #                 text=f"Получать расписание на сегодня {'✅' if user_settings.get('reminder_today', True) else '❌'}",
        #                 callback_data=f"settings#bool${not user_settings.get('reminder_today', True)}$reminder_today"
        #             )]]
        #         elif i % 4 == 0 and i != 0:
        #             keyboard += [[InlineKeyboardButton(
        #                 text=f"Получать расписание на завтра {'✅' if not user_settings.get('reminder_today', True) else '❌'}",
        #                 callback_data=f"settings#bool${not user_settings.get('reminder_today', True)}$reminder_today"
        #             )]]

        #         for time_value, time_label in choices[i:i+count_in_row]:
        #             row.append(InlineKeyboardButton(
        #                 text=f"{time_label}",
        #                 callback_data=f"set_reminder_time#{time_value}",
        #             ))

        #         keyboard += [row]
        #     return InlineKeyboardMarkup(keyboard)
            
        text = messages.ask_reminder_time
        reply_markup = None # get_actual_markup(user_settings)
        
        # !КОСТЫЛЬ
        context.user_data.update(dict(
            send_settings=False,
            settings_text=text,
            # get_actual_markup=get_actual_markup,
        ))

    
        await update_message.reply_text(
            text=text,
            reply_markup=reply_markup,
        )
    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Callback handlers                           |
    @ensure_user_settings()
    async def set_reminder_time(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        update_message = update.message or update.callback_query.message
        query = update.callback_query

        await query.answer()
        
        user: User = context.user_data.get('user_model')
        
        time_value = query.data.split("#")[-1]
        time_label = Subscriber.TimeChoices.get_label(time_value)
        
        
        if not time_label:
            await update_message.edit_text(
                "Ошибка! Неправильно передано значение",
                parse_mode='HTML',
            )
            return


        subscriber: Subscriber = Subscriber.objects.get_or_create(
            user_id=user.id,
        )
        subscriber.set_scheduled_time(time_value)
        await self.update_user_settings(update, context)
        
        
        # !КОСТЫЛЬ
        # context.user_data.update(dict(
        #     send_settings=True,
        #     settings_text=None,
        #     get_actual_markup=None,
        # ))
    
    
        await update_message.edit_text(
            messages.user_scheduled_reminder_template(time_label),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[self.delegate_button_template("⚙️ Настройки", "settings")],[self.menu_button]])
        )
        
        
    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |                       Logic                               |

    
    async def schedule_broadcast(self, context: "ContextTypes.DEFAULT_TYPE"):
        session: 'requests.Session' = context.bot_data.get('session')
        if not session: return
    
        subscriber_list = Subscriber.get_active_subscribers()
        group_ids = set(sub.user.group_id for sub in subscriber_list)
        
        if not group_ids: return
        
        
        # group_id = list(group_ids)[0]
        
        # print(context.bot_data.get('session'))
        
        # response: dict = ScheduleModule.get_schedule_by_group_id(
        #     session=session,
        #     group_id=group_id
        # )
        
        # message = ScheduleModule.get_message_schedule(response, is_daily=True)
        
        # print(message)
        
        
        

    # * |___________________________________________________________|
