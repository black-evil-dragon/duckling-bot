from telegram.ext import  ApplicationBuilder

from db.core import Database

from core.db import Database as DeprecatedDatabase
from core.models.user import User

from core.settings import COMMANDS, setup_commands
from core.session import Session


from dotenv import load_dotenv
from utils.logger import setup_logger
from utils.scheduler import JobManager


import os
import logging



load_dotenv() 


log: 'logging.Logger' = None
job_manager = JobManager()
            

class Bot:

    session_manager: 'Session' = None
    db_manager = None


    def __init__(self, token: str, api_id: str, api_key: str, db_filename: str = ''):
        self.token = token

        self.app = ApplicationBuilder().token(self.token).post_init(self.post_init).build()

        #* Session
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
        job_manager.start()
            

    # * ____________________________________________________________
    # * |                       Setups                              |
    def setup_modules(self, modules_config, job_manager=job_manager):
        modules_config(self.app, job_manager=job_manager)
        log.info("+ Модули установлены")


    def setup_database(self, filename='db.sqlite3'):
        try:
            if not os.path.exists(filename):
                # raise FileNotFoundError(f"Файл {filename} не найден")
                log.error(f'Файл {filename} не найден!')
                
                open(filename, 'w').close()
                log.info(f'Создан новый файл базы данных: {filename}')
                
            
            self.db_manager = DeprecatedDatabase(filename=filename)
            self.app.bot_data.update({'db': self.db_manager})
            
            filename = 'db_test.sqlite3'
            Database.init(url=f'sqlite:///{filename}')
            # Database.init(url='postgresql:///user:password@localhost/dbname')
            User.create_all()
            log.debug(f'+ Созданы таблицы в базе данных: {User}')


            log.info(f'+ База данных успешно подключена к файлу: {filename}')

        except Exception as e:
            log.error(f'- Не удалось загрузить базу данных: {e}')

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
    log = setup_logger()

    main()