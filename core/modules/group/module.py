
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

from core.modules.group import messages



log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)


#* Module ________________________________________________________________________
class GroupModule(BaseModule):

    def __init__(self):
        log.info("GroupModule initialized")


    def setup(self, application: 'Application'):
        # Command
        application.add_handler(CommandHandler("set_group", self.ask_institute))

        # Message
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_selection))



    # * ____________________________________________________________
    # * |                   User utils                             |
    def clear_choices(self, context: 'ContextTypes.DEFAULT_TYPE'):
        for key in ['selected_institute', 'selected_course', 'selected_group']:
            context.user_data.pop(key, None)


    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Command handlers                            |

    #? /set_group - Изменяет группу пользователя
    async def ask_institute(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        self.clear_choices(context)

        buttons = [[KeyboardButton(str(institute))] for institute in GROUP_IDS.keys()]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            messages.choose_institute,
            reply_markup=reply_markup
        )


    async def ask_course(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        institute = context.user_data["selected_institute"]

        courses = GROUP_IDS[institute]
        buttons = [[KeyboardButton(str(course))] for course in courses]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            messages.dialog_choose_course(institute),
            reply_markup=reply_markup
        )


    async def ask_group(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        institute = context.user_data["selected_institute"]
        course = context.user_data["selected_course"]

        groups = GROUP_IDS[institute][course]
        buttons = [[KeyboardButton(str(group))] for group in groups]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            messages.choose_group,
            reply_markup=reply_markup
        )

    # * |___________________________________________________________|





    # * ____________________________________________________________
    # * |               Message handlers                            |

    async def handle_selection(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        
        # Заходим в блок только если у нас нет группы в контексте пользователя
        if "selected_group" not in context.user_data:

            # Выбор института
            if "selected_institute" not in context.user_data:
                await self.selection_institute(update, context)
            
            # Выбор курса
            elif "selected_course" not in context.user_data:
                await self.selection_course(update, context)
            
            # Выбор группы
            else:
                await self.selection_group(update, context)


    #* ---------- Select institute 
    async def selection_institute(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text
    
        if user_input not in GROUP_IDS.keys():
            
            await update.message.reply_text(
                messages.institute_wrong_choice,
                reply_markup=ReplyKeyboardRemove()
            )

            await self.ask_institute(update, context)

        else:
            context.user_data["selected_institute"] = user_input

            await self.ask_course(update, context)




    #* ---------- Select course 
    async def selection_course(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text

        institute = context.user_data["selected_institute"]
        courses = GROUP_IDS[institute]
        
        # Наверное тут лучше через метод проверять и убрать лишние if elif, но пока так
        if not user_input.isdigit():
            await update.message.reply_text(
                messages.course_wrong_choice
            )

            await self.ask_course(update, context)
        
        elif int(user_input) not in courses:
            await update.message.reply_text(
                messages.course_wrong_choice
            )

            await self.ask_course(update, context)
        
        else:
            context.user_data["selected_course"] = int(user_input)

            await self.ask_group(update, context)
            


    #* ---------- Select group 
    async def selection_group(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text

        institute = context.user_data["selected_institute"]
        course = context.user_data["selected_course"]
        groups = GROUP_IDS[institute][course]
        
        if user_input not in groups:
            await update.message.reply_text(
                messages.group_wrong_choice,
                reply_markup=ReplyKeyboardRemove()
            )

            await self.ask_group(update, context)

        else:
            group_id = groups[user_input]
            context.user_data["selected_group"] = group_id
            
            await update.message.reply_text(
                messages.result_choices(institute, course, user_input),
                reply_markup=ReplyKeyboardRemove()
            )
            
    # * |___________________________________________________________|