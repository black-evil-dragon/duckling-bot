
#* Telegram bot framework ________________________________________________________________________
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram import Update

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import ContextTypes
from telegram.ext import filters

#* Core ________________________________________________________________________
from core.modules.base import BaseModule
from core.modules.base.decorators import ensure_dialog_branch, ensure_user_settings, send_on_error, set_dialog_branch
from core.modules.group import messages

from core.settings.commands import CommandNames
from core.data.group import SUBGROUP_IDS, Group
from core.models import User as UserModel

#* Other packages ________________________________________________________________________
from utils.logger import get_logger
from slugify import slugify
from typing import TYPE_CHECKING, Any, Dict, List


if TYPE_CHECKING:
    from core.modules.schedule import ScheduleModule


log = get_logger()


#* Module ________________________________________________________________________
class GroupModule(BaseModule):
    group_ids = Group.load_from_json().get('groups')
    groups: Dict[str, Any] = {}
    group_keys: List[str] = []


    def setup(self):
        # Command
        self.application.add_handler(CommandHandler(CommandNames.SET_GROUP, self.ask_institute))
        self.application.add_handler(CommandHandler(CommandNames.SET_SUBGROUP, self.ask_subgroup))

        # Message
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_group_selection),
            group=1
        )
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.selection_subgroup),
            group=2
        )

        for institute in self.group_ids:
            for course in self.group_ids[institute]:
                for group_name, group_id in self.group_ids[institute][course].items():
                    slug = slugify(group_name)
                    self.groups[slug] = dict(
                        group_name=group_name,
                        group_id=group_id,
                        institute=institute,
                        course=course
                    )
                    self.group_keys.append(slug)





    # * ____________________________________________________________
    # * |                   User utils                             |


    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Command handlers                            |
    #? /set_group - Изменяет группу пользователя
    @classmethod
    @ensure_user_settings(need_update=True)
    @set_dialog_branch('institute_selection', reset_attempt=True)
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
    @set_dialog_branch('course_selection', reset_attempt=False)
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



    @set_dialog_branch('group_selection', reset_attempt=False)
    async def ask_group(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE', group_search: List[str] = None):
        institute = context.user_data.get("selected_institute")
        course = context.user_data.get("selected_course")

        if group_search is None:
            groups = list(GroupModule.group_ids[institute][course])
        else:
            groups = [group_name for group_name in group_search]

            if len(groups) == 1:
                await self.selection_group(update, context, groups_search=groups)
                return

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
    # ! Костыльно
    async def handle_group_selection(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        # Выбор института
        if context.user_data.get("selected_institute") is None:
            await self.selection_institute(update, context)

        # Выбор курса
        elif context.user_data.get("selected_course") is None:
            await self.selection_course(update, context)

        # Выбор группы
        elif context.user_data.get("selected_group") is None:
            await self.selection_group(update, context)


    #* ---------- Select institute
    @ensure_user_settings()
    @ensure_dialog_branch('institute_selection')
    async def selection_institute(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text

        groups_search = self.search_group_by_name(user_input)

        if len(groups_search) >= 1:
            await self.ask_group(update, context, groups_search)
            context.user_data["selected_institute"] = 'Не выбран'
            context.user_data["selected_course"] =  'Не выбран'
            return True

        elif user_input not in self.group_ids.keys():
            await update.message.reply_text(
                messages.institute_wrong_choice,
            )

            return


        context.user_data["selected_institute"] = user_input

        await self.ask_course(update, context)
        return True



    #* ---------- Select course
    @ensure_dialog_branch('course_selection')
    async def selection_course(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user_input = update.message.text

        institute = context.user_data.get("selected_institute")
        courses = self.group_ids.get(institute, [])


        # Наверное тут лучше через метод проверять и убрать лишние if elif, но пока так
        if not user_input.isdigit() or user_input not in courses:
            await update.message.reply_text(
                messages.course_wrong_choice
            )
            return


        context.user_data["selected_course"] = user_input

        await self.ask_group(update, context)
        return True



    #* ---------- Select group
    @ensure_user_settings()
    @ensure_dialog_branch('group_selection', stop_after=True)
    async def selection_group(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE', groups_search : List[str]= None):
        user: UserModel = context.user_data.get("user_model")
        user_input = update.message.text

        institute = context.user_data["selected_institute"]
        course = context.user_data["selected_course"]

        if groups_search is None:
            groups_search = self.search_group_by_name(user_input)

        if len(groups_search) == 0:
            await update.message.reply_text(
                messages.group_wrong_choice,
            )
            return

        if len(groups_search) > 1:
            groups = [group_name for group_name in groups_search]
            buttons = [[KeyboardButton(group)] for group in groups]
            reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

            await update.message.reply_text(
                messages.choose_group,
                reply_markup=reply_markup
            )
            # Коммент ниже
            return dict(stop_dialog=False)


        #? if len(groups_search) == 1
        slug = slugify(groups_search[0])
        group: Dict[str, Any] = self.groups.get(slug, {})

        group_id = group.get('group_id')
        course = group.get('course')
        institute = group.get('institute')

        context.user_data["selected_institute"] = institute
        context.user_data["selected_course"] = course

        # ! КОСТЫЛЬ
        # Фишки быстрого поиска расписания, вышло не очень, но хоть как-то оно работает...
        if context.bot_data.get('quick_schedule') is not None:
            context.bot_data['quick_schedule'].update(dict(
                target_id=group_id,
                target_type='student'
            ))

            await context.bot_data['quick_schedule'].get('callback', lambda update, context: log.error('Не установлен callback для быстрого расписания'))(update, context)

            return dict(stop_dialog=True)



        context.user_data["selected_group"] = group_id





        user.set_group(group_id)

        await update.message.reply_text(
            messages.result_choices(institute, course, groups_search[0]),
            reply_markup=ReplyKeyboardRemove()
        )

        # Столкнулся с тем, что этод метод должен продолжить работу
        # Пока код находит среди ввода группы, но и при этом не завершать
        # работу dialog с помощью stop_after=True
        # Поэтому я решил сделать так
        # Делать return dict(...), чтобы return value был не None
        # и при этом можно было разделить успешность работы
        return dict(stop_dialog=True)



    #* ---------- Select subgroup
    @ensure_user_settings()
    @ensure_dialog_branch('subgroup_selection', stop_after=True)
    @send_on_error()
    async def selection_subgroup(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        user: UserModel = context.user_data.get("user_model")
        user_input = update.message.text

        if user_input not in SUBGROUP_IDS:
            await update.message.reply_text(
                messages.subgroup_wrong_choice,
            )

            return

        selected_subgroup = SUBGROUP_IDS[user_input]

        context.user_data["selected_subgroup"] = selected_subgroup

        user.set_subgroup(selected_subgroup, set_subgroup_lock=True)


        await update.message.reply_text(
            messages.result_subgroup_choice(user_input),
            reply_markup=ReplyKeyboardRemove()
        )
        return True

    # * |___________________________________________________________|


    def search_group_by_name(self, user_input: str, course: str = None, institute: str = None) -> List[str]:
        slug = slugify(user_input)
        result = []


        for group_key in self.group_keys:
            if slug in group_key:
                group: Dict[str, Any] = self.groups[group_key]
                group_name = group.get('group_name')

                if group_name:
                    if course is not None and group.get('course') != course:
                        continue
                    if institute is not None and group.get('institute') != institute:
                        continue

                    result.append(group_name)


        return result