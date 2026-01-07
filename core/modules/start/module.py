
#* Telegram bot framework ________________________________________________________________________
from telegram import Update
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram import InlineKeyboardButton

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram.ext import filters

from telegram.error import BadRequest

#* Core ________________________________________________________________________
from core.models.subscriber import Subscriber
from core.models.user import User
from core.modules.base.messages import get_commands_text, start_text
from core.modules.reminder.module import ReminderModule
from core.settings.commands import CommandNames

from core.modules.base import BaseModule
from core.modules.base.decorators import ensure_user_settings

from core.modules.group.module import GroupModule
from core.modules.schedule.module import ScheduleModule

from core.modules.start import messages
from core.modules.reminder import messages as reminder_messages
#* Other packages ________________________________________________________________________
from utils.logger import get_logger


log = get_logger()



#* Module ________________________________________________________________________
class StartModule(BaseModule):
    def setup(self) -> None:
        self.application.add_handler(MessageHandler(
            filters.ALL,
            self.update_user_settings
        ), group=-1)

        self.application.add_handler(MessageHandler(
            ~filters.COMMAND,
            self.some_text
        ), group=-1)

        self.application.add_handler(CommandHandler(CommandNames.START, self.start))
        self.application.add_handler(CommandHandler(CommandNames.HELP, self.help))
        self.application.add_handler(CommandHandler(CommandNames.MENU, self.get_menu))
        self.application.add_handler(CommandHandler(CommandNames.SETTINGS, self.send_settings))


        self.application.add_handler(CallbackQueryHandler(self.handle_settings, pattern="^settings#"))
        self.application.add_handler(CallbackQueryHandler(self.handle_inline_commands, pattern="^delegate#"))



    @classmethod
    async def handle_inline_commands(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        MENU_COMMANDS = cls.get_menu_commands(context)

        query = update.callback_query
        await query.answer()

        # Получаем номер недели из callback_data
        command = str(query.data.split('#')[-1])
        
        # ! КОСТЫЛЬ 
        handler_map = {
            command: func for command, _, func in MENU_COMMANDS
        }

        # !КОСТЫЛЬ
        handler_map.update({
            CommandNames.SET_REMINDER: ReminderModule.ask_reminder_time,
            CommandNames.SHOW_REMINDER: ReminderModule.show_reminder_info,
        })


        if command in handler_map:
            await handler_map[command](update, context)

        elif command == 'menu':
            await cls.get_menu(update, context)



    @classmethod
    async def show_command_keyboard(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE') -> None:
        buttons = context.bot_data['command_keyboard']
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        update_message = update.message or update.callback_query.message

        await update_message.reply_text(
            messages.show_command_keyboard,
            reply_markup=reply_markup

        )



    # * ____________________________________________________________
    # * |               Command handlers                            |
    @classmethod
    async def start(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        await update.message.reply_text(
            start_text,
            parse_mode='HTML',
            disable_web_page_preview=True,
        )

        await cls.show_command_keyboard(update, context)


    @classmethod
    async def help(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        update_message = update.message or update.callback_query.message

        await update_message.reply_text(get_commands_text())
        await cls.show_command_keyboard(update, context)


    @classmethod
    def get_menu_commands(cls, context: 'ContextTypes.DEFAULT_TYPE'):
        user_settings: dict = context.user_data.get('user_settings', {})

        # ! КОСТЫЛЬ - название команд отличается от CommandNames
        MENU_COMMANDS = (
            (None, None, None),
            ("help", "Помощь", cls.help),
            (None, None, None),

            ("schedule", "Расписание", ScheduleModule.schedule_handler),
            ("today", "На сегодня", ScheduleModule.get_schedule_day) if user_settings.get('show_week', False) else ("week", "На неделю", ScheduleModule.get_schedule_week),
            ("tomorrow", "На завтра", ScheduleModule.get_schedule_next_day),

            ("set_group", "Установить группу", GroupModule.ask_institute),
            (None, None, None),
            ("set_subgroup", "Установить подгруппу", GroupModule.ask_subgroup),

            ("settings", "Настройки", cls.send_settings),
        )

        return MENU_COMMANDS


    @classmethod
    @ensure_user_settings(need_update=True)
    async def get_menu(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        update_message = update.message or update.callback_query.message
        MENU_COMMANDS = cls.get_menu_commands(context)

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=desc, callback_data=f"delegate#{cmd}") for cmd, desc, _ in MENU_COMMANDS[i:i+3] if cmd]
            for i in range(0, len(MENU_COMMANDS), 3)
        ])

        await update_message.reply_text(
            "📋 Главное меню:",
            reply_markup=reply_markup
        )



    @classmethod
    @ensure_user_settings(is_await=False)
    def get_settings(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_settings: dict = context.user_data.get('user_settings', {})
        # _, user_scheduled_time_label = context.user_data.get('scheduled_time', {})


        SETTINGS_COMMANDS = (
            None,
            (
                f"settings#bool${not user_settings.get('subgroup_lock', False)}$subgroup_lock",
                f"Только подгруппа {'✅' if user_settings.get('subgroup_lock', False) else '❌'}",
            ),
            None,


            # Связанные настройки, если включен один, другой выключить
            (
                f"settings#bool${not user_settings.get('show_week', False)}$show_week",
                f"П.у неделя {'✅' if user_settings.get('show_week', False) else '❌'}",
            ),
            None,
            (
                f"settings#bool${not user_settings.get('show_week', False)}$show_week",
                f"П.у день {'✅' if not user_settings.get('show_week', False) else '❌'}",
            ),


            None,
            (
                f"settings#bool${not user_settings.get('reminder', False)}$reminder",
                f"📢 Рассылка {'✅' if user_settings.get('reminder', False) else '❌'}",
            ),
            None,

            None,
            (f"delegate#{CommandNames.SET_REMINDER}", "⏰ Выбрать время"),
            (f"delegate#{CommandNames.SHOW_REMINDER}", CommandNames.SHOW_REMINDER.label),

            None,
            (f"delegate#{CommandNames.MENU}", "📍 Меню"),
            None,
        )

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text=command[1], callback_data=f"{command[0]}") for command in SETTINGS_COMMANDS[i:i+3] if command]
            for i in range(0, len(SETTINGS_COMMANDS), 3)
        ])


    @classmethod
    @ensure_user_settings(need_update=True)
    async def send_settings(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        update_message = update.message or update.callback_query.message
        reply_markup = cls.get_settings(update, context)

        # ? Что это такое???
        # Это прикол, который позволяет отправлять
        # свой markup с text через контекст
        context.user_data.update(dict(
            send_custom_settings=False,
            settings_text=None,
            get_actual_markup=None
        ))

        await update_message.reply_text(
            messages.settings_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Message handlers                            |
    async def some_text(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        if not context.user_data.get('is_command_process', False):
            await self.show_command_keyboard(update, context)

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Callback handlers                            |
    @staticmethod
    @ensure_user_settings(need_update=True)
    async def handle_settings(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        update_message = update.message or update.callback_query.message
        query = update.callback_query

        await query.answer()

        user: User = context.user_data.get('user_model')
        user_settings: dict = context.user_data.get('user_settings', {})

        # * Определение настройки
        command = query.data.split('#')[-1]
        value_type, value, setting = command.split('$')


        # * Особенности поведения
        # !КОСТЫЛЬ
        # В теории, это надо вынести в отдельный метод
        # Тогда здесь можно было бы написать типо
        # | if callback_checker is not None:
        # |     callback_checker(command_info)

        # * Дефолтные проверки
        if setting == 'subgroup_lock' and context.user_data.get('selected_subgroup') is None:
            await GroupModule.ask_subgroup(update, context)

        if setting == 'reminder':
            subscriber: "Subscriber" = Subscriber.objects.update_or_create(
                user_id=user.id,
                # defaults=dict(
                #     is_active=user_settings.get('reminder', False)
                # )
            )

            if context.user_data.get('selected_group') is None:
                await context.bot.send_message(
                    chat_id=user.user_id,
                    text=reminder_messages.group_is_not_chosen,
                )
                # await GroupModule.ask_institute(update, context)
                return


            if subscriber.schedule_time is None:
                await context.bot.send_message(
                    chat_id=user.user_id,
                    text=reminder_messages.time_is_not_chosen,
                )
                # await ReminderModule.ask_reminder_time(update, context)
                return


            await ReminderModule.sign_subscriber(subscriber, user_settings.get('reminder', False), user=user)


        # * Обновление данных
        user_settings = user.set_setting(setting, value, value_type)
        context.user_data.update(dict(user_settings=user_settings))


        # !КОСТЫЛЬ.. Наверное
        # См метод send_settings
        # * Надстройка для отправки своего markup и text
        reply_markup = StartModule.get_settings(update, context)
        text = messages.settings_text

        if context.user_data.get('send_custom_settings', False):
            get_custom_markup = context.user_data.get('get_custom_markup')

            if get_custom_markup:
                reply_markup = get_custom_markup(user_settings)

            text = context.user_data.get('custom_settings_text', messages.settings_text)


        # * Отправка сообщения
        try:
            await update_message.edit_text(
                text=text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

        except BadRequest:
            log.error('Ошибка при редактировании сообщения, возможно, сообщение не изменено.')
            # log.debug('Текст ошибки:', exc_info=True)
            return

    # * |___________________________________________________________|