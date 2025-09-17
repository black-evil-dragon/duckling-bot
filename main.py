#
#* Telegram bot framework ________________________________________________________________________
from telegram.ext import  ApplicationBuilder


#* DB ________________________________________________________________________
from db.core import Database


#* Core ________________________________________________________________________
from core.models import User, Subscriber
from core.settings import COMMANDS, setup_commands
from core.session import Session


#* Other packages ________________________________________________________________________
from utils.logger import setup_logger
from utils.scheduler import JobManager

from dotenv import load_dotenv

import os
import logging




            

class Bot:

    session_manager: 'Session' = None
    job_manager: 'JobManager' = None



    def __init__(self, token: str, api_id: str, api_key: str, db_filename: str = 'db.sqlite3'):
        self.token = token

        self.app = ApplicationBuilder().token(self.token).post_init(self.post_init).build()

        # * Session
        self.session_manager: 'Session' = Session(
            id=api_id,
            key=api_key,  
        )
        self.app.bot_data.update({'session': self.session_manager})

        # * Job manager
        self.job_manager = JobManager()
        self.app.bot_data.update({'job_manager': self.job_manager})
        

        # * Database
        self.setup_database(db_filename)
        # self.app.bot_data.update({'database': Database}) # ? Это вообще нужно?


    async def post_init(self, application):
        await setup_commands(application, COMMANDS)
        self.job_manager.start()
            

    # * ____________________________________________________________
    # * |                       Setups                              |
    def setup_modules(self, modules_config):
        modules_config(self.app)
        # log.info("+ Модули установлены")


    def setup_database(self, filename):
        try:
            log.info('Подключение к базе данных')
            if not os.path.exists(filename):
                log.error(f'| Файл {filename} не найден!')
                
                open(filename, 'w').close()
                log.info(f'| Создан новый файл базы данных: {filename}')
            
        
            # Init db
            Database.init(url=f'sqlite:///{filename}')

            # Create tables
            User.create_all()
            Subscriber.create_all()



            log.info(f'+ База данных успешно подключена к файлу: {filename}')

        except Exception as e:
            log.error(f'+ Не удалось загрузить базу данных: {e}')

    # * |___________________________________________________________|




    # * ____________________________________________________________
    # * |                        Run                                |
    def run(self):
        log.info("Бот запускается...")
        self.app.run_polling()


def main():
    try:
        from core.settings.config import BOT_TOKEN, DB_FILEPATH, API_KEY, API_ID
        
        # * Инициализация ---------------------------------------------------------
        bot = Bot(
            token=BOT_TOKEN,
            api_id=API_ID,
            api_key=API_KEY,
            db_filename=DB_FILEPATH
        )


        # * Подключаем модули и запускаем ----------------------------------------
        try:
            from core.modules import setup_modules
            

            bot.setup_modules(setup_modules)
            
            bot.run()

        except Exception as error:
            return log.exception(f'Не удалось загрузить модули: {str(error)}')
        

    except ImportError:
        log.error('Не найден файл конфигурации [./utils/config.py].')
        log.error('| - Создайте файл конфигурации на основе [./utils/config.template.py]')
        return
    
    


if __name__ == "__main__":
    load_dotenv() 

    log: 'logging.Logger' = None
    log = setup_logger()

    main()