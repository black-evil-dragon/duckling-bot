
#* Telegram bot framework ________________________________________________________________________
from telegram import Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application

#* Core ________________________________________________________________________
from core.modules.base import BaseModule


#* Other packages ________________________________________________________________________
from utils.scheduler import JobManager


import logging
import threading
import time


log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)



class ReminderModule(BaseModule):
    
    jobs = {}
    
    job_manager: 'JobManager' = None
    
    def __init__(self, job_manager: 'JobManager' = None):
        log.info("ReminderModule initialized")
        
        
        if job_manager is not None:
            self.job_manager = job_manager
            
            self.job_manager.create_cron_job(
                'monday-broadcast',
                callback=self.morning_broadcast,
                time_data=dict(seconds=5)
            )
        
        
        
    def setup(self, application: 'Application'):
        pass
    
    
    
    
    
    




    # * ____________________________________________________________
    # * |               Command handlers                            |

    # * |___________________________________________________________|


    # * ____________________________________________________________
    # * |               Callback handlers                           |
    # ...
    # * |___________________________________________________________|
    
    
    
    # * ____________________________________________________________
    # * |                       Logic                               |
    def morning_broadcast(self):
        log.info('Morning!')
    # * |___________________________________________________________|