
#* Telegram bot framework ________________________________________________________________________
from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes

import telegram

#* Core ________________________________________________________________________
from core.data.weekdays import WeekDay
from core.models.user import User
from core.modules.base import BaseModule, strf_time_mask
from core.modules.base.decorators import ensure_user_settings
from core.modules.group.module import GroupModule

from core.session import Session
from core.settings.commands import CommandNames


from . import messages


#* Other packages ________________________________________________________________________
from datetime import datetime, timedelta
from datetime import date as DateType
from typing import Any, Dict, Literal, Tuple
from utils.logger import get_logger

import traceback
import requests


log = get_logger()



#* Module ________________________________________________________________________
class ScheduleModule(BaseModule):

    template_manager = messages.TemplateManager()
    session: requests.Session = None


    def setup(self):
        self.session = self.application.bot_data.get('session')

        # * Чисто экспериментальный код, думаю как можно сделать лучше
        self.HANDLERS = (
            # Command
            CommandHandler(CommandNames.SCHEDULE, self.schedule_handler),
            CommandHandler(CommandNames.WEEK, self.get_schedule_week),
            CommandHandler(CommandNames.TODAY, self.get_schedule_day),
            CommandHandler(CommandNames.TOMORROW, self.get_schedule_next_day),
            CommandHandler(CommandNames.DATE, self.ask_date),

            # Callback
            CallbackQueryHandler(self.schedule_day_callback, pattern="^schedule_day#"),
            CallbackQueryHandler(self.schedule_week_callback, pattern="^schedule_week#"),
            CallbackQueryHandler(self.handle_calendar_callback, pattern="^calendar_nav#")
        )

        self.application.add_handlers(self.HANDLERS)



    # * ____________________________________________________________
    # * |                    Utils                                  |
    def fetch_data(
        self,
        path: str,
        params: dict,
    ) -> dict:
        # log.debug(f'Отправлен запрос: {path}')
        response = self.session.post(
            path,
            json=params
        )

        try:
            response.raise_for_status()
        except Exception as error:
            log.error(f'Ошибка при запросе: {error}. Данные ответа: {response}. Данные запроса: {params}')

        response_json: dict = response.json()

        if response_json.get('last_update'):
            response_json['data']['last_update'] = datetime.strptime(response_json['last_update'], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M:%S")


        # log.debug(f'Получен ответ: {response_json}')
        return response_json



    @staticmethod
    def get_schedule_query(
        group_id: int = None,
        user_data: dict = None,
        date_start: datetime = datetime.today(),
        date_end: datetime = None,
    ):
        if user_data is None:
            user_data = {}

        user_settings: dict = user_data.get('user_settings', {})

        params = dict(
            group_id=str(user_data.get('selected_group', None) or group_id),
            selected_lesson_type="typical",
        )


        if date_end is not None:
            params.update(dict(
                date_start=date_start.strftime(strf_time_mask),
                date_end=date_end.strftime(strf_time_mask),
            ))

        else:
            params.update(dict(
                date=date_start.strftime(strf_time_mask),
            ))


        if user_settings.get('subgroup_lock', False) and user_data.get('selected_subgroup'):
            params.update(dict(
                subgroup=user_data.get('selected_subgroup')
            ))


        return params



    @staticmethod
    def get_prev_next_day(current_day: 'DateType', strftime=False) -> Tuple[DateType, DateType] | Tuple[str, str]:
        """
        Возвращает кортеж дат +- день от текущего дня

        args:
            `current_day` (DateType): День, от которого идет отсчет

        returns:
            Tuple[date, date]: Кортеж дат
        """

        if current_day.weekday() != WeekDay.MONDAY:
            prev_date = current_day - timedelta(days=1)
        else:
            prev_date = current_day - timedelta(days=2)


        if current_day.weekday() != WeekDay.SATURDAY:
            next_date = current_day + timedelta(days=1)
        else:
            next_date = current_day + timedelta(days=2)

        if strftime:
            prev_date = prev_date.strftime(strf_time_mask)
            next_date = next_date.strftime(strf_time_mask)

        return prev_date, next_date


    @staticmethod
    def get_prev_next_week(current_day: DateType) -> Tuple[str, str]:
        """
        Возвращает кортеж дат +- номер недели от текущего дня
        """
        # Предыдущая неделя
        prev_period = current_day - timedelta(days=7)
        prev_week = prev_period.isocalendar().week
        prev_year = prev_period.isocalendar().year

        # Следующая неделя
        next_period = current_day + timedelta(days=7)
        next_week = next_period.isocalendar().week
        next_year = next_period.isocalendar().year

        return f'{prev_week}.{prev_year}', f'{next_week}.{next_year}'




    def get_schedule_by_target_id(
        self,
        target_id: int,

        schedule_type: str = "day",
        user_data: dict = None,

        date_start: datetime = datetime.today(),
        date_end: datetime = None,

    ) -> dict:
        if user_data is None: user_data = {}

        if schedule_type == "day" and date_start.weekday() == WeekDay.SUNDAY:
            date_start += timedelta(days=1)


        data = dict(
            group_id=target_id,
            date_start=date_start,
            date_end=date_end,
            user_data=user_data
        )


        request = dict(
            path=f"schedule/{schedule_type}/",
            params=self.get_schedule_query(**data),
        )


        response_data: dict = self.fetch_data(**request)
        data: Dict[str, Any] = response_data.get('data', {})

        # чуть костыльно, но норм
        # Пробрасываем шаблон
        data.update(dict(message_template=user_data.get('user_settings', {}).get('message_template', "default")))

        return data


    @classmethod
    def get_message_schedule(cls, data: dict, is_daily: bool = True, date: "DateType" = datetime.today()) -> dict:
        additional_buttons = None
        data_type = 'day' if is_daily else 'weeks'

        template_name: Literal['default', 'compact', 'minimal'] = data.get('message_template')
        template = cls.template_manager.get_template(template_name)


        if is_daily and date.weekday() == WeekDay.SUNDAY:
            date += timedelta(days=1)


        message = template.get_message(data, data_type=data_type)
        prev_key, next_key = cls.get_prev_next_day(date, strftime=True) if is_daily else cls.get_prev_next_week(date)


        if is_daily:
            callback_data = 'schedule_day'
            entity = 'День'
            additional_buttons = [
                messages.get_refresh_button(f'{callback_data}#{date.strftime(strf_time_mask)}'),
                messages.get_schedule_button()
            ]

        else: # then for period
            callback_data = 'schedule_week'
            entity = 'Неделя'
            additional_buttons = [
                messages.get_refresh_button(
                    f'{callback_data}#{date.isocalendar().week}.{date.isocalendar().year}'
                ),
                messages.get_schedule_button()
            ]


        return dict(
            text=message,
            parse_mode='HTML',
            reply_markup=messages.use_paginator(
                callback_data=callback_data,
                entity=entity,
                prev_key=prev_key,
                next_key=next_key,

                additional_buttons=additional_buttons
            )
        )


    def generate_schedule_content(self, user: User, date: DateType, date_end : DateType = None):
        schedule_type = 'day'
        is_daily = True

        if date_end is not None:
            schedule_type = 'period'
            is_daily = False

        args = dict(
            target_id=user.group_id,
            schedule_type=schedule_type,
            date_start=date,
            date_end=date_end,
            user_data=dict(
                user_id=user.user_id,
                **user.get_selected_data(),
                user_settings=user.get_user_settings(),
            )
        )

        schedule: dict = self.get_schedule_by_target_id(**args)
        message = self.get_message_schedule(schedule, is_daily=is_daily, date=date)

        return message
    # * |___________________________________________________________|



    # * ____________________________________________________________
    # * |               Command handlers                            |
    @classmethod
    async def ask_date(cls, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        update_message = update.message or update.callback_query.message

        await update_message.reply_text(
            text=messages.schedule_ask_date,
            reply_markup=cls.generate_calendar()
        )



    @ensure_user_settings()
    async def schedule_handler(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        schedule_week = context.user_data.get('user_settings', {}).get('show_week', False)

        if schedule_week:
            await self.get_schedule_week(update, context)
        else:
            await self.get_schedule_day(update, context)



    @ensure_user_settings()
    async def get_schedule_next_day(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        context.user_data['need_tomorrow'] = True

        await self.get_schedule_day(update, context)



    @ensure_user_settings()
    async def get_schedule_day(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')
        update_message = update.message or update.callback_query.message

        # Проверяем наличие сессии
        if not session:
            await update_message.reply_text(messages.session_error)
            return

        # Проверяем наличие группы
        if not context.user_data.get('selected_group', False):
            await GroupModule.ask_institute(update, context)
            return


        try:
            date = datetime.now().date()
            user: User = context.user_data.get('instance')


            if context.user_data.get('need_tomorrow', False):
                date += timedelta(days=1)
                context.user_data.update(dict(
                    need_tomorrow=False
                ))


            content = self.generate_schedule_content(user, date)

            await update_message.reply_text(**content)


        except Exception:
            traceback.print_exc()
            await update_message.reply_text(messages.server_error)



    @ensure_user_settings()
    async def get_schedule_week(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')

        update_message = update.message or update.callback_query.message


        if not session:
            await update_message.reply_text(messages.session_error)
            return


        if not context.user_data.get('selected_group', False):
            await GroupModule.ask_institute(update, context)
            return


        try:
            today = datetime.now().date()
            date_start = today - timedelta(days=today.weekday())
            date_end = date_start + timedelta(days=5)
            user: User = context.user_data.get('instance')


            content = self.generate_schedule_content(user, date_start, date_end)


            try:
                await update_message.reply_text(**content)

            except telegram.error.BadRequest as exception:
                if exception.message == 'Message is not modified' or 'Message is not modified' in str(exception):
                    log.error(f'Ошибка отправки сообщения [{exception.message}]')
                    log.warning('Пробуем отправить еще раз!')

                    await context.bot.send_message(
                        chat_id=context.user_data.get('user_id'),
                        **content
                    )
                    return

                log.exception(f'Неизвестная ошибка при отправке сообщения! {exception}')

            except Exception as exception:
                log.exception(f'Неизвестная ошибка при отправке сообщения! {exception}')


        except Exception:
            traceback.print_exc()
            await update_message.reply_text(messages.server_error, parse_mode='HTML')

    # * |___________________________________________________________|




    # * ____________________________________________________________
    # * |               Callback handlers                           |
    @ensure_user_settings()
    async def handle_calendar_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        date_str = await super().handle_calendar_callback(update, context) # Важно для использования календаря

        if date_str is not None:
            if not context.user_data.get('selected_group', False):
                await GroupModule.ask_institute(update, context)
                return

            date = datetime.strptime(date_str, strf_time_mask)
            user: User = context.user_data.get('instance')

            content = self.generate_schedule_content(user, date)

            await context.bot.send_message(
                chat_id=user.user_id,
                **content
            )



    @ensure_user_settings()
    async def schedule_week_callback(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')

        query = update.callback_query
        query_data = query.data.split('#')
        query_week_number = query_data[-1]
        user: User = context.user_data.get('instance')

        await query.answer()


        if not session:
            await query.edit_message_text(messages.session_error)
            return

        if not context.user_data.get('selected_group', False):
            await GroupModule.ask_institute(update, context)
            return


        week_number, year = query_week_number.split('.')

        date_start = DateType.fromisocalendar(int(year), int(week_number), 1)
        date_end = date_start + timedelta(days=5)

        content = self.generate_schedule_content(user, date_start, date_end)


        try:
            await query.edit_message_text(**content)

        except telegram.error.BadRequest as exception:
            if exception.message == 'Message is not modified' or 'Message is not modified' in str(exception):
                log.error(f'Ошибка отправки сообщения [{exception.message}]')
                log.warning('Пробуем отправить еще раз!')

                await context.bot.send_message(
                    chat_id=context.user_data.get('user_id'),
                    **content
                )
                return

            log.exception(f'Неизвестная ошибка при отправке сообщения! {exception}')

        except Exception as exception:
            log.exception(f'Неизвестная ошибка при отправке сообщения! {exception}')



    @ensure_user_settings()
    async def schedule_day_callback(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        session: 'Session' = context.bot_data.get('session')

        query = update.callback_query
        query_data = query.data.split('#')
        query_date = datetime.strptime(query_data[-1], strf_time_mask)
        user: User = context.user_data.get('instance')

        await query.answer()


        if not session:
            await query.edit_message_text(messages.session_error)
            return

        if not context.user_data.get('selected_group', False):
            await GroupModule.ask_institute(update, context)
            return


        content = self.generate_schedule_content(user, query_date)


        try:
            await query.edit_message_text(**content)

        except telegram.error.BadRequest as exception:
            if exception.message == 'Message is not modified' or 'Message is not modified' in str(exception):
                log.error(f'Ошибка отправки сообщения [{exception.message}]')
                log.warning('Пробуем отправить еще раз!')

                await context.bot.send_message(
                    chat_id=context.user_data.get('user_id'),
                    **content
                )
                return

            log.exception(f'Неизвестная ошибка при отправке сообщения! {exception}')

        except Exception as exception:
            log.exception(f'Неизвестная ошибка при отправке сообщения! {exception}')

    # * |___________________________________________________________|