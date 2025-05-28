
#* Telegram bot framework ________________________________________________________________________
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, User
from telegram import Update

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import ContextTypes, Application
from telegram.ext import filters

#* Core ________________________________________________________________________
from core.modules.base import BaseModule
from core.data.group import GROUP_IDS, SUBGROUP_IDS, Group
from core.db import Database

#* Other packages ________________________________________________________________________
import logging

from core.modules.group import messages



log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)


#* Module ________________________________________________________________________
class GroupModule(BaseModule):
    group_ids = Group.load_from_json().get('groups')

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
    @BaseModule.command_process(True)
    async def ask_institute(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        GroupModule.clear_choices(context)
        update_message = update.message or update.callback_query.message

        context.user_data.update(dict(
            is_group_selection=True,
            is_command_process=True
        ))

        buttons = [
            [
                KeyboardButton(str(institute))
                for institute in list(GroupModule.group_ids)[i:i+3]
            ] for i in range(0, len(list(GroupModule.group_ids)), 3)
        ]

        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        
        await update_message.reply_text(
            messages.choose_institute,
            reply_markup=reply_markup
        )


    @staticmethod
    async def ask_course(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        institute = context.user_data["selected_institute"]
        courses = list(GroupModule.group_ids[institute])

        buttons = [
            [
                KeyboardButton(str(value))
                for value in courses[i:i+3]
            ] for i in range(0, len(courses), 3)
        ]

        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            messages.dialog_choose_course(institute),
            reply_markup=reply_markup
        )


    @staticmethod
    async def ask_group(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        institute = context.user_data["selected_institute"]
        course = context.user_data["selected_course"]

        groups = list(GroupModule.group_ids[institute][course])

        buttons = [
            [
                KeyboardButton(str(value))
                for value in groups[i:i+3]
            ] for i in range(0, len(groups), 3)
        ]


        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            messages.choose_group,
            reply_markup=reply_markup
        )


    @staticmethod
    @BaseModule.command_process(True)
    async def ask_subgroup(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        update_message = update.message or update.callback_query.message
        context.user_data.pop('selected_subgroup', None)

        context.user_data.update(dict(
            is_subgroup_selection=True,
            is_command_process=True
        ))

        subgroups = list(SUBGROUP_IDS)

        buttons = [
            [
                KeyboardButton(str(value))
                for value in subgroups[i:i+3]
            ] for i in range(0, len(subgroups), 3)
        ]

        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

        await update_message.reply_text(
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
    
        if user_input not in self.group_ids.keys():
            
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
        courses = self.group_ids[institute]
        
        # Наверное тут лучше через метод проверять и убрать лишние if elif, но пока так
        if not user_input.isdigit():
            await update.message.reply_text(
                messages.course_wrong_choice
            )

            await self.ask_course(update, context)
        
        elif user_input not in courses:
            await update.message.reply_text(
                messages.course_wrong_choice
            )

            await self.ask_course(update, context)
        
        else:
            context.user_data["selected_course"] = user_input

            await self.ask_group(update, context)
            


    #* ---------- Select group
    async def selection_group(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text

        institute = context.user_data["selected_institute"]
        course = context.user_data["selected_course"]
        groups = self.group_ids[institute][course]

        groups_search = Group.find_group_by_name(groups=[group for group in groups], group_name=user_input)


        if groups.get(user_input) is not None:
            group_id = groups[user_input]

            context.user_data["selected_group"] = group_id
            context.user_data['is_group_selection'] = False
            context.user_data["is_command_process"] = False

            user = update.effective_user
            self.save_user_data(user, context)
            
            await update.message.reply_text(
                messages.result_choices(institute, course, user_input),
                reply_markup=ReplyKeyboardRemove()
            )
        elif len(groups_search) == 1:
            group_id = groups[groups_search[0]]

            context.user_data["selected_group"] = group_id
            context.user_data['is_group_selection'] = False
            context.user_data["is_command_process"] = False

            user = update.effective_user
            self.save_user_data(user, context)
            
            await update.message.reply_text(
                messages.result_choices(institute, course, groups_search[0]),
                reply_markup=ReplyKeyboardRemove()
            )

        elif len(groups_search) > 1:
            buttons = [[KeyboardButton(group)] for group in groups_search]
            reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

            await update.message.reply_text(
                messages.choose_group,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                messages.group_wrong_choice,
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
            
            BaseModule.set_command_process(False, context)

            await update.message.reply_text(
                messages.result_subgroup_choice(SUBGROUP_IDS[user_input]),
                reply_markup=ReplyKeyboardRemove()
            )
            
    # * |___________________________________________________________|