
#* Telegram bot framework ________________________________________________________________________
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram import Update

from telegram.ext import CommandHandler,MessageHandler
from telegram.ext import ContextTypes, Application
from telegram.ext import filters

#* Core ________________________________________________________________________
from core.modules.base import BaseModule

from core.data.group import GROUP_IDS

#* Other packages ________________________________________________________________________
import logging



log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)


#* Module ________________________________________________________________________
class GroupModule(BaseModule):

    def __init__(self):
        log.info("GroupModule initialized")


    def setup(self, application: 'Application'):
        # Command
        application.add_handler(CommandHandler("set_group", self.ask_course))

        # Message
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_selection))



    # * ____________________________________________________________
    # * |               Command handlers                            |

    #? /set_group - Изменяет группу пользователя
    async def ask_course(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        buttons = [[KeyboardButton(str(course))] for course in GROUP_IDS.keys()]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "Выберите ваш курс:",
            reply_markup=reply_markup
        )

    # * |___________________________________________________________|





    # * ____________________________________________________________
    # * |               Message handlers                            |

    async def handle_selection(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        # Выбор института
        if "selected_institute" not in context.user_data:
            await self.selection_institute(update, context)
        
        # Выбор курса
        elif "selected_course" not in context.user_data:
            await self.selection_course(update, context)
        
        # ЭВыбор группы
        else:
            await self.selection_group(update, context)


    #* ---------- Select institute 
    async def selection_institute(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text
    
        if user_input in GROUP_IDS:
            context.user_data["selected_institute"] = user_input
            
            # Получаем доступные курсы для выбранного института
            courses = list(GROUP_IDS[user_input].keys())
            buttons = [[KeyboardButton(str(course))] for course in courses]
            reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                f"Выбран институт {user_input}. Теперь выберите курс:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "Пожалуйста, выберите институт из предложенных вариантов.",
                reply_markup=ReplyKeyboardRemove()
            )


    #* ---------- Select course 
    async def selection_course(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text

        institute = context.user_data["selected_institute"]
        courses = GROUP_IDS[institute]
        
        if user_input.isdigit() and int(user_input) in courses:
            course = int(user_input)
            context.user_data["selected_course"] = course
            
            # Получаем группы для выбранного курса
            groups = courses[course]
            buttons = [[KeyboardButton(group)] for group in groups.keys()]
            reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                f"Выбран курс {course}. Теперь выберите группу:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "Пожалуйста, выберите курс из предложенных вариантов.",
                reply_markup=ReplyKeyboardRemove()
            )


    #* ---------- Select group 
    async def selection_group(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text

        institute = context.user_data["selected_institute"]
        course = context.user_data["selected_course"]
        groups = GROUP_IDS[institute][course]
        
        if user_input in groups:
            group_id = groups[user_input]
            context.user_data["group_id"] = group_id
            
            await update.message.reply_text(
                f"Институт: {institute}\nКурс: {course}\nГруппа: {user_input} (ID: {group_id})\n\nНастройки сохранены!",
                reply_markup=ReplyKeyboardRemove()
            )
            # Очищаем временные данные
            context.user_data.clear()
            context.user_data["group_id"] = group_id  # Сохраняем только ID группы
        else:
            await update.message.reply_text(
                "Пожалуйста, выберите группу из предложенных вариантов.",
                reply_markup=ReplyKeyboardRemove()
            )
            


    # * |___________________________________________________________|