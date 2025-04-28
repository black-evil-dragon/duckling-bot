
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
        user_input = update.message.text

        # Если пользователь еще не выбрал курс, сохраняем его и спрашиваем группу
        if "selected_course" not in context.user_data:
            if user_input.isdigit() and int(user_input) in GROUP_IDS:
                course = int(user_input)
                context.user_data["selected_course"] = course
                
                # Получаем группы для выбранного курса
                groups = GROUP_IDS[course]
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
        
        # Если курс уже выбран, сохраняем группу
        else:
            course = context.user_data["selected_course"]
            groups = GROUP_IDS[course]
            
            if user_input in groups:
                group_id = groups[user_input]
                context.user_data["group_id"] = group_id
                
                await update.message.reply_text(
                    f"Группа {user_input} (ID: {group_id}) успешно установлена!",
                    reply_markup=ReplyKeyboardRemove()
                )
                # Очищаем временные данные
                del context.user_data["selected_course"]
            else:
                await update.message.reply_text(
                    "Пожалуйста, выберите группу из предложенных вариантов.",
                    reply_markup=ReplyKeyboardRemove()
                )


    # * |___________________________________________________________|