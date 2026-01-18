
#* Telegram bot framework ________________________________________________________________________
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram import Update

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import ContextTypes
from telegram.ext import filters

#* Core ________________________________________________________________________
from core.models import User
from core.modules.base import BaseModule
from core.modules.base.decorators import ensure_dialog_branch, ensure_user_settings, set_dialog_branch
from core.modules.teacher import messages

from core.settings.commands import CommandNames

#* Other packages ________________________________________________________________________
from utils.logger import get_logger
from slugify import slugify
from typing import Any, Dict, List

import requests


log = get_logger()


#* Module ________________________________________________________________________
class TeacherModule(BaseModule):
    session: requests.Session = None

    teachers = {}

    def setup(self):
        self.session = self.application.bot_data.get('session')


        self.application.add_handler(
            CommandHandler(CommandNames.SET_TEACHER, self.ask_teacher)
        )
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.selection_teacher),
            group=3
        )

        self.set_teachers()


    def set_teachers(self):
        teachers: List[Dict[str, str]] = self.fetch('teacher/all/').get('teachers')

        for teacher in teachers:
            slug = slugify(teacher.get('name'))
            self.teachers[slug] = dict(
                id=teacher.get('id'),
                name=teacher.get('name'),
                degree=teacher.get('degree')
            )

    # * ____________________________________________________________
    # * |               Utils                                       |

    def fetch(
        self,
        path: str,
        params: dict = None,
    ) -> dict:
        if params is None:
            params = {}

        response = self.session.post(
            path,
            json=params
        )

        try:
            response.raise_for_status()
        except Exception as error:
            log.error(f'Ошибка при запросе: {error}. Данные ответа: {response.content.decode("unicode_escape")}. Данные запроса: {params}')
            return

        response_json: dict = response.json()


        # log.debug(f'Получен ответ: {response_json}')
        return response_json


    def search_teacher(self, teacher_name):
        pass

    # * |___________________________________________________________|


    # * ____________________________________________________________
    # * |               Command handlers                            |
    @ensure_user_settings(need_update=True)
    @set_dialog_branch('teacher_selection', reset_attempt=True)
    async def ask_teacher(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        context.user_data['selected_teacher'] = None

        update_message = update.message or update.callback_query.message

        reply_markup = ReplyKeyboardMarkup([
            [
                KeyboardButton(self.teachers[teacher].get('name'))
                for teacher in list(self.teachers)[i:i+2]
            ] for i in range(0, len(list(self.teachers)[:150]), 2)
        ], one_time_keyboard=True, resize_keyboard=True)

        # * Return
        await update_message.reply_text(
            messages.choose_teacher_fio,
            reply_markup=reply_markup
        )

    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Message handlers                            |
    @ensure_user_settings()
    @ensure_dialog_branch('teacher_selection')
    async def selection_teacher(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        update_message = update.message or update.callback_query.message
        user_input = update_message.text
        user: User = context.user_data.get("user_model")

        teachers: List[Dict[str, Any]] = self.fetch('teacher/search/', dict(
            teacher_name=user_input
        )).get('data')


        if not teachers:
            await update_message.reply_text(
                messages.empty_teachers,
            )
            return

        elif len(teachers) > 1:
            await update_message.reply_text(
                messages.choose_teacher_fio,
                reply_markup=messages.get_teachers_reply_markup(teachers)
            )
            return True

        elif len(teachers) == 1:
            teacher = teachers[0]
            teacher_id = teacher.get('id')


            # ! КОСТЫЛЬ
            # Фишки быстрого поиска расписания, вышло не очень, но хоть как-то оно работает...
            if context.bot_data.get('quick_schedule') is not None:
                context.bot_data['quick_schedule'].update(dict(
                    target_id=teacher_id,
                    target_type='teacher'
                ))

                await update.message.reply_text(
                    messages.result_choices(teacher),
                    reply_markup=ReplyKeyboardRemove()
                )


                await context.bot_data['quick_schedule'].get('callback', lambda update, context: log.error('Не установлен callback для быстрого расписания'))(update, context)

                return dict(stop_dialog=True)



            user.set_teacher(teacher_id)
            context.user_data['selected_teacher'] = teacher_id


            await update.message.reply_text(
                messages.result_choices(teacher),
                reply_markup=ReplyKeyboardRemove()
            )

            await update.message.reply_text(
                text=self.menu_back,
                reply_markup=InlineKeyboardMarkup([[self.menu_button]])
            )

            return dict(stop_dialog=True)
    # * |___________________________________________________________|

    # * ____________________________________________________________
    # * |               Callback handlers                           |
    # ...

    # * |___________________________________________________________|