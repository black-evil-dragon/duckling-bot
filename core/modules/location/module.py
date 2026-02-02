# * Telegram bot framework ________________________________________________________________________
from typing import Any, Dict, List
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram import Update

from telegram.ext import MessageHandler
from telegram.ext import ContextTypes
from telegram.ext import filters

# * Core ________________________________________________________________________
from core.modules.base import BaseModule
from core.modules.base.decorators import (
    ensure_dialog_branch,
    ensure_user_settings,
    set_dialog_branch,
)
from core.modules.location import messages

# * Other packages ________________________________________________________________________
from utils.logger import get_logger
from core.session import Session

log = get_logger()




# * Module ________________________________________________________________________
class LocationModule(BaseModule):
    session: Session = None

    teachers = {}
    last_selected_audience: str | None = None

    def setup(self):
        self.session = self.application.bot_data.get("session")

        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.selection_building),
            group=6,
        )
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.selection_audience),
            group=5,
        )



    # * ____________________________________________________________
    # * |               Command handlers                            |
    @ensure_user_settings()
    @set_dialog_branch("building_selection", reset_attempt=True)
    async def ask_building(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["selected_building"] = None

        update_message = update.message or update.callback_query.message

        await update_message.reply_text(
            text=messages.choose_building,
            reply_markup=ReplyKeyboardMarkup(
                [[str(i) for i in [*range(1, 14), "с/к 1", "СК2"]]],
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )



    @set_dialog_branch("audience_selection", reset_attempt=True)
    async def ask_audience(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        update_message = update.message or update.callback_query.message

        await update_message.reply_text(
            text=messages.choose_audience, reply_markup=ReplyKeyboardRemove()
        )
    # * |___________________________________________________________|





    # * ____________________________________________________________
    # * |               Message handlers                            |
    @ensure_dialog_branch("building_selection", stop_after=True)
    async def selection_building(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text

        locations = self.session.fetch(
            "location/search/", dict(building=user_input)
        ).get("data")

        if not locations:
            await update.message.reply_text(
                messages.empty_buildings,
            )
            return

        context.user_data["selected_building"] = user_input

        return dict(callback=self.ask_audience)


    @ensure_dialog_branch("audience_selection", stop_after=True)
    async def selection_audience(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text

        locations: List[Dict[str, Any]] = self.session.fetch(
            "location/search/",
            dict(building=context.user_data["selected_building"], audience=user_input),
        ).get("data")
        audiences = [location.get('audience') for location in locations]

        if not locations:
            await update.message.reply_text(messages.empty_audiences)
            return

        elif len(locations) > 1 and self.last_selected_audience is None:
            self.last_selected_audience = user_input
            await update.message.reply_text(
                messages.choose_audience,
                reply_markup=messages.get_locations_reply_markup(locations),
            )
            return dict(stop_dialog=False)


        elif len(locations) > 1 and user_input in audiences:
            self.last_selected_audience = None
            locations = list(filter(lambda location: location.get('audience') == user_input, locations))

        # ! КОСТЫЛЬ
        # Мало того, что оно работает чисто в режиме quick, так еще и старые костыли, оно работает
        # Фишки быстрого поиска расписания, вышло не очень, но хоть как-то оно работает...
        location = locations[0]
        location_id = location.get("id")

        if context.bot_data.get("quick_schedule") is not None:
            context.bot_data["quick_schedule"].update(
                dict(target_id=location_id, target_type="location")
            )

            await update.message.reply_text(
                messages.result_choices(location), reply_markup=ReplyKeyboardRemove()
            )

            await context.bot_data["quick_schedule"].get(
                "callback",
                lambda update, context: log.error(
                    "Не установлен callback для быстрого расписания"
                ),
            )(update, context)

            return dict(stop_dialog=True)

    # * |___________________________________________________________|




    # * ____________________________________________________________
    # * |               Callback handlers                            |

    # * |___________________________________________________________|