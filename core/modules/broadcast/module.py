
#* Telegram bot framework ________________________________________________________________________
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update

from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram.ext import filters

#* Core ________________________________________________________________________
from core.models.user import User
from core.modules.base import BaseModule
from core.modules.base.decorators import ensure_dialog_branch, ensure_user_settings, set_dialog_branch, try_send_message
from core.modules.broadcast import messages

from core.settings.commands import CommandNames


#* Other packages ________________________________________________________________________
from utils.logger import get_logger
from typing import List
from anyio import sleep

log = get_logger()


#* Module ________________________________________________________________________
class BroadcastModule(BaseModule):

    def setup(self):
        # self.application.add_handler(CommandHandler(CommandNames.AUTH, self.ask_admin_type))
        self.application.add_handler(CommandHandler(CommandNames.BROADCAST, self.ask_broadcast_message))

        self.application.add_handler(CallbackQueryHandler(self.broadcast_auth_callback, pattern="^broadcast_auth#"))
        self.application.add_handler(CallbackQueryHandler(self.cancel_callback, pattern="^broadcast_cancel"))


        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.selection_message), group=7)




    # * ____________________________________________________________
    # * |               Command handlers                            |
    @ensure_user_settings(need_update=True)
    @try_send_message()
    async def ask_admin_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        update_message = update.message or update.callback_query.message

        return update_message.edit_text, dict(
            text=messages.broadcast_auth_ask_type,
            reply_markup=messages.auth_type_buttons,
        )



    @ensure_user_settings(need_update=True, role_access='teacher')
    @try_send_message()
    @set_dialog_branch('broadcast_message_selection')
    async def ask_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        update_message = update.message or update.callback_query.message

        return update_message.edit_text, dict(
            text=messages.broadcast_ask_message,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="broadcast_cancel")]]),
        )

    # * |___________________________________________________________|




    # * ____________________________________________________________
    # * |               Message handlers                            |

    @ensure_dialog_branch('broadcast_message_selection', stop_after=True)
    async def selection_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_input = update.message.text
        users: List[User] = User.objects.all()

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user.user_id,
                    text=user_input,
                    disable_web_page_preview=True,
                )

                await sleep(.25)
            except Exception as error:
                log.error(f'Ошибка рассылки сообщения! {error}')

        return True

    # * |___________________________________________________________|




    # * ____________________________________________________________
    # * |               Callback handlers                            |

    @ensure_user_settings()
    @try_send_message()
    async def broadcast_auth_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        query_data = query.data.split('#')[-1]



    @set_dialog_branch('broadcast_message_selection', False)
    async def cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            self.menu_back,
            reply_markup=InlineKeyboardMarkup([[self.menu_button]])
        )
    # * |___________________________________________________________|




