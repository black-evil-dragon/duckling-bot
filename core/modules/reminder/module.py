# * Telegram bot framework ________________________________________________________________________
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application

# * Core ________________________________________________________________________
from core.models.subscriber import Subscriber
from core.models.user import User
from core.modules.base import BaseModule


# * Other packages ________________________________________________________________________
from core.modules.base.decorators import ensure_user_settings
from core.modules.reminder import messages
from core.settings.commands import CommandNames
from utils.logger import get_logger
from utils.scheduler import JobManager


log = get_logger()


class ReminderModule(BaseModule):
    jobs = {}

    job_manager: "JobManager" = None
    
    

    def setup(self, application: "Application"):
        application.add_handler(CommandHandler(CommandNames.SHOW_REMINDER, self.show_reminder_info))
        application.add_handler(CommandHandler(CommandNames.SET_REMINDER, self.ask_reminder_time))
        
        application.add_handler(CallbackQueryHandler(self.set_reminder_time, pattern="^set_reminder_time#"))

        self.job_manager = application.bot_data.get("job_manager", None)
        
        for task_name, time in Subscriber.cron_data.items():
            self.job_manager.create_cron_job(
                task_name,
                callback=self.morning_broadcast,
                job_type="cron",
                time_data=dict(
                    **time,
                    day_of_week="mon-sat"
                ),
            )

    # * ____________________________________________________________
    # * |               Command handlers                            |
    @classmethod
    @ensure_user_settings()
    async def show_reminder_info(cls, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        update_message = update.message or update.callback_query.message
        time_value, time_label = context.user_data.get("scheduled_time")

        message = messages.user_scheduled_reminder_template(time_label)

        await update_message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup([[cls.delegate_button_template(messages.choose_reminder_time_button, f"delegate#{CommandNames.SET_REMINDER}")]])
        )


    @classmethod
    @ensure_user_settings()
    async def ask_reminder_time(cls, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        update_message = update.message or update.callback_query.message
        choices = Subscriber.TimeChoices.choices()

        keyboard = []
        count_in_row = 2

        for i in range(0, len(choices), count_in_row):
            row = []
            for time_value, time_label in choices[i:i+count_in_row]:
                row.append(InlineKeyboardButton(
                    text=f"{time_label}",
                    callback_data=f"set_reminder_time#{time_value}",
                ))
            keyboard += [row]
            
    
        await update_message.reply_text(
            messages.ask_reminder_time,
            reply_markup=InlineKeyboardMarkup(keyboard),
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
            user_id=user.user_id,
            defaults=dict(
                username=user.username,
            )
        )
        subscriber.set_scheduled_time(time_value)
        await self.update_user_settings(update, context)
    
    
        await update_message.edit_text(
            messages.user_scheduled_reminder_template(time_label),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[self.delegate_button_template("⚙️ Настройки", "settings")],[self.menu_button]])
        )
        
        
    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |                       Logic                               |
    def morning_broadcast(self):
        log.info("Morning broadcast !!!!!!!!!!")

    # * |___________________________________________________________|
