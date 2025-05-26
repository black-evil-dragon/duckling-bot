from typing import List, Tuple
from telegram import BotCommand
from telegram.ext import Application, ApplicationBuilder

from core.db import Database
from core.settings import COMMANDS, setup_commands

from core.session import Session
from utils.logger import setup_logger

import os
import logging


from dotenv import load_dotenv
load_dotenv() 


log: 'logging.Logger' = None

class Bot:

    session_manager: 'Session' = None
    db_manager = None


    def __init__(self, token: str, api_id: str, api_key: str, test_run: bool = False, db_filename: str = ''):
        self.token = token

        self.app = ApplicationBuilder().token(self.token).post_init(self.post_init).build()

        #* Session
        if not test_run:
            #? В Github Actions мы не будем использовать сессии
            self.session_manager: 'Session' = Session(
                id=api_id,
                key=api_key,  
            )

        self.app.bot_data.update({'session': self.session_manager})


        #* Database
        if db_filename:
            self.setup_database(db_filename)


    async def post_init(self, application):
        await setup_commands(application, COMMANDS)
            

    # * ____________________________________________________________
    # * |                       Setups                              |
    def setup_modules(self, modules_config):
        modules_config(self.app)
        log.info("Модули установлены")


    def setup_database(self, filename):
        try:
            if not os.path.exists(filename): raise FileNotFoundError(f"Файл {filename} не найден")
            
            self.db_manager = Database(filename=filename)
            self.app.bot_data.update({'db': self.db_manager})

            log.info(f'База данных успешно подключена к файлу: {filename}')

        except Exception as e:
            log.error(f'Не удалось загрузить базу данных: {e}')

    # * |___________________________________________________________|




    # * ____________________________________________________________
    # * |                        Run                                |
    def run(self):
        log.info("Бот запускается...")
        self.app.run_polling()


def main():
    try:
        from utils.config import BOT_TOKEN, TEST_RUN, DB_FILENAME, API_KEY, API_ID

        # * Инициализация ---------------------------------------------------------
        bot = Bot(
            token=BOT_TOKEN,
            api_id=API_ID,
            api_key=API_KEY,
            test_run=TEST_RUN,
            db_filename=DB_FILENAME
        )


        # * Подключаем модули и запускаем ----------------------------------------
        try:
            from core.modules import setup_modules
            bot.setup_modules(setup_modules)

            if TEST_RUN:
                return log.info('Включен режим тестовый запуск')
            
            bot.run()

        except Exception as error:
            return log.error(f'Не удалось загрузить модули: {str(error)}')
        

    except ImportError:
        log.error('Не найден файл конфигурации [./utils/config.py].')
        log.error('| - Создайте файл конфигурации на основе [./utils/config.template.py]')
        return 
    
    


if __name__ == "__main__":
    log = setup_logger()

    main()