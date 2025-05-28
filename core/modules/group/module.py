
#* Telegram bot framework ________________________________________________________________________
from typing import Any, Dict
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, User
from telegram import Update

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import ContextTypes, Application
from telegram.ext import filters

#* Core ________________________________________________________________________
from core.modules.base import BaseModule
from core.data.group import GROUP_IDS, SUBGROUP_IDS
from core.db import Database

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
        application.add_handler(CommandHandler("set_group", GroupModule.ask_institute))
        application.add_handler(CommandHandler("set_subgroup", GroupModule.ask_subgroup))

        # Message
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_selection))



    # * ____________________________________________________________
    # * |                   User utils                             |
    @staticmethod
    def clear_choices(context: 'ContextTypes.DEFAULT_TYPE'):
        for key in ['selected_institute', 'selected_course', 'selected_group']:
            context.user_data.pop(key, None)

    @staticmethod
    def save_user_data(user: 'User', context: 'ContextTypes.DEFAULT_TYPE'):
        if context.bot_data.get('db', None) is None: return

        db: 'Database' = context.bot_data.get('db')

        user_data = {
            "id": user.id,
            "is_bot": user.is_bot,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
        }

        if context.user_data.get("selected_group", None) is not None:
            user_data.update(dict(group_id=context.user_data.get("selected_group", None)))
        
        if context.user_data.get('selected_subgroup', None) is not None:
            user_data.update(dict(subgroup_id=context.user_data.get("selected_subgroup", None)))

        db.add_or_update_user(user_data)

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Command handlers                            |

    #? /set_group - Изменяет группу пользователя
    @staticmethod
    async def ask_institute(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        GroupModule.clear_choices(context)

        context.user_data["is_group_selection"] = True

        buttons = [[KeyboardButton(str(institute))] for institute in GROUP_IDS.keys()]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            messages.choose_institute,
            reply_markup=reply_markup
        )


    @staticmethod
    async def ask_course(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        institute = context.user_data["selected_institute"]

        courses = GROUP_IDS[institute]
        buttons = [[KeyboardButton(str(course))] for course in courses]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            messages.dialog_choose_course(institute),
            reply_markup=reply_markup
        )

    @staticmethod
    async def ask_group(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        institute = context.user_data["selected_institute"]
        course = context.user_data["selected_course"]

        groups = GROUP_IDS[institute][course]
        buttons = [[KeyboardButton(str(group))] for group in groups]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            messages.choose_group,
            reply_markup=reply_markup
        )


    @staticmethod
    async def ask_subgroup(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        context.user_data.pop('selected_subgroup', None)

        context.user_data["is_subgroup_selection"] = True


        buttons = [[KeyboardButton(str(subgroup_id))] for subgroup_id in SUBGROUP_IDS]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            messages.choose_subgroup,
            reply_markup=reply_markup
        )

    # * |___________________________________________________________|





    # * ____________________________________________________________
    # * |               Message handlers                            |

    async def handle_selection(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):

        # Заходим в блок только если у нас нет группы в контексте пользователя
        if context.user_data.get('is_group_selection', False):

            # Выбор института
            if "selected_institute" not in context.user_data:
                await self.selection_institute(update, context)
            
            # Выбор курса
            elif "selected_course" not in context.user_data:
                await self.selection_course(update, context)
            
            # Выбор группы
            else:
                await self.selection_group(update, context)

        if context.user_data.get('is_subgroup_selection', False):
            await self.selection_subgroup(update, context)


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
            context.user_data['is_group_selection'] = False

            user = update.effective_user
            self.save_user_data(user, context)
            
            await update.message.reply_text(
                messages.result_choices(institute, course, user_input),
                reply_markup=ReplyKeyboardRemove()
            )


    #* ---------- Select subgroup
    async def selection_subgroup(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text

        if user_input not in SUBGROUP_IDS:
            await update.message.reply_text(
                messages.subgroup_wrong_choice,
                reply_markup=ReplyKeyboardRemove()
            )

            await self.ask_subgroup(update, context)

        else:
            context.user_data["selected_subgroup"] = SUBGROUP_IDS[user_input]
            context.user_data['is_subgroup_selection'] = False

            user = update.effective_user

            self.save_user_data(user, context)
            

            await update.message.reply_text(
                messages.result_subgroup_choice(SUBGROUP_IDS[user_input]),
                reply_markup=ReplyKeyboardRemove()
            )
            
    # * |___________________________________________________________|