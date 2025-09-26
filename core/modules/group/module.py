
#* Telegram bot framework ________________________________________________________________________
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram import Update

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import ContextTypes, Application
from telegram.ext import filters

#* Core ________________________________________________________________________
from core.modules.base import BaseModule
from core.modules.base.decorators import ensure_dialog_branch, ensure_user_settings, set_dialog_branch
from core.modules.group import messages

from core.settings.commands import CommandNames
from core.data.group import SUBGROUP_IDS, Group
from core.models import User as UserModel

#* Other packages ________________________________________________________________________
from utils.logger import get_logger


log = get_logger()


#* Module ________________________________________________________________________
class GroupModule(BaseModule):
    group_ids = Group.load_from_json().get('groups')



    def setup(self, application: 'Application'):
        # Command
        application.add_handler(CommandHandler(CommandNames.SET_GROUP, self.ask_institute))
        application.add_handler(CommandHandler(CommandNames.SET_SUBGROUP, self.ask_subgroup))

        # Message
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_group_selection),
            group=1
        )
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.selection_subgroup),
            group=2
        )



    # * ____________________________________________________________
    # * |                   User utils                             |
    @staticmethod
    def clear_choices(context: 'ContextTypes.DEFAULT_TYPE'):
        for key in ['selected_institute', 'selected_course', 'selected_group']:
            context.user_data.pop(key, None)

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Command handlers                            |

    #? /set_group - Изменяет группу пользователя
    @classmethod
    @ensure_user_settings(need_update=True)
    @set_dialog_branch('group_selection')
    async def ask_institute(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        cls.clear_choices(context)
        update_message = update.message or update.callback_query.message

        # * Set keyboard
        reply_markup = ReplyKeyboardMarkup([
            [
                KeyboardButton(str(institute))
                for institute in list(cls.group_ids)[i:i+3]
            ] for i in range(0, len(list(cls.group_ids)), 3)
        ], one_time_keyboard=True, resize_keyboard=True)
        
        
        # * Return
        await update_message.reply_text(
            messages.choose_institute,
            reply_markup=reply_markup
        )


    @classmethod
    async def ask_course(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        institute = context.user_data.get("selected_institute")
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


    @classmethod
    async def ask_group(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        institute = context.user_data.get("selected_institute")
        course = context.user_data.get("selected_course")

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


    @classmethod
    @set_dialog_branch('subgroup_selection')
    async def ask_subgroup(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        update_message = update.message or update.callback_query.message
        context.user_data.pop('selected_subgroup', None)

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
    @ensure_dialog_branch('group_selection')
    async def handle_group_selection(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        # Выбор института
        if context.user_data.get("selected_institute") is None:
            await self.selection_institute(update, context)
        
        # Выбор курса
        elif context.user_data.get("selected_course") is None:
            await self.selection_course(update, context)
        
        # Выбор группы
        else:
            await self.selection_group(update, context)


    #* ---------- Select institute 
    @ensure_dialog_branch('group_selection')
    async def selection_institute(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text

        if user_input not in self.group_ids.keys():
            
            await update.message.reply_text(
                messages.institute_wrong_choice,
                reply_markup=ReplyKeyboardRemove()
            )

            await self.ask_institute(update, context)
            return


        context.user_data["selected_institute"] = user_input

        await self.ask_course(update, context)
        return True



    #* ---------- Select course 
    @ensure_dialog_branch('group_selection')
    async def selection_course(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text

        institute = context.user_data.get("selected_institute")
        courses = self.group_ids.get(institute, [])
        
        
        # Наверное тут лучше через метод проверять и убрать лишние if elif, но пока так
        if not user_input.isdigit() or user_input not in courses:
            await update.message.reply_text(
                messages.course_wrong_choice
            )

            await self.ask_course(update, context)
            return
        

        context.user_data["selected_course"] = user_input

        await self.ask_group(update, context)
        return True
            


    #* ---------- Select group
    @ensure_user_settings()
    @ensure_dialog_branch('group_selection', stop_after=True)
    async def selection_group(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user: UserModel = context.user_data.get("user_model")
        user_input = update.message.text

        institute = context.user_data["selected_institute"]
        course = context.user_data["selected_course"]
        groups = self.group_ids[institute][course]

        groups_search = Group.find_group_by_name(groups=[group for group in groups], group_name=user_input)


        if groups.get(user_input) is not None:
            group_id = groups[user_input]

        elif len(groups_search) == 1:
            group_id = groups[groups_search[0]]
            user_input = groups_search[0]

        elif len(groups_search) > 1:
            buttons = [[KeyboardButton(group)] for group in groups_search]
            reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

            await update.message.reply_text(
                messages.choose_group,
                reply_markup=reply_markup
            )
            return True
        else:
            await update.message.reply_text(
                messages.group_wrong_choice,
            )
            return

        context.user_data["selected_group"] = group_id

        user.set_group(group_id)
        
        await update.message.reply_text(
            messages.result_choices(institute, course, user_input),
            reply_markup=ReplyKeyboardRemove()
        )
        return True



    #* ---------- Select subgroup
    @ensure_user_settings()
    @ensure_dialog_branch('subgroup_selection', stop_after=True)
    async def selection_subgroup(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user: UserModel = context.user_data.get("user_model")
        user_input = update.message.text

        if user_input not in SUBGROUP_IDS:
            await update.message.reply_text(
                messages.subgroup_wrong_choice,
                reply_markup=ReplyKeyboardRemove()
            )

            await self.ask_subgroup(update, context)
            return

        selected_subgroup = SUBGROUP_IDS[user_input]
        
        context.user_data["selected_subgroup"] = selected_subgroup

        user.set_subgroup(selected_subgroup)
        

        await update.message.reply_text(
            messages.result_subgroup_choice(user_input),
            reply_markup=ReplyKeyboardRemove()
        )
        return True
            
    # * |___________________________________________________________|