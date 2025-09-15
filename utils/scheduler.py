from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.cron import CronTrigger

import logging
import asyncio


log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)

class JobManager:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(jobstores=dict(default=MemoryJobStore()), timezone='Europe/Moscow')
        self.jobs = {}
        self._started = False

        log.info("Планировщик инициализирован")
        
    
    def start(self):
        log.info('- Запускаем планировщик...')
        self._started = True
        self.scheduler.start()
        
        log.info('+ Планировщик запущен')
    
    
    def create_cron_job(self, name: str, callback, job_type: str = 'interval', time_data: dict = None):
        """Создает или пересоздает cron-задачу"""
        if time_data is None:
            time_data = {'hour': 0, 'minute': 0}
        
        # Если задача уже существует - удаляем её
        if name in self.jobs:
            log.warning(f'Событие {name} уже существует! Удаляем его')
            self.remove_job(name)
        
        try:
            # Создаем новую задачу
            job = self.scheduler.add_job(
                callback,
                job_type,
                **time_data,
                id=name,
                name=name
            )
            
            self.jobs[name] = job.id
            log.info(f'Создана задача {name} с расписанием: {time_data}')
            return True
            
        except Exception as e:
            log.error(f'Ошибка создания задачи {name}: {e}')
            return False
    
    
    def remove_job(self, name: str):
        """Удаляет задачу по имени"""
        if name in self.jobs:
            try:
                self.scheduler.remove_job(self.jobs[name])
                del self.jobs[name]
                log.info(f'Задача {name} удалена')
                return True

            except Exception as e:
                log.error(f'Ошибка удаления задачи {name}: {e}')
                return False

        else:
            log.warning(f'Задача {name} не найдена')
            return False
    
    
    def list_jobs(self):
        """Возвращает список всех задач"""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger)
            })
        return jobs_info
    
    
    def get_job(self, name: str):
        """Получает информацию о задаче"""
        if name in self.jobs:
            return self.scheduler.get_job(self.jobs[name])
        return None
    
    
    def update_job(self, name: str, time_dict: dict):
        """Обновляет расписание задачи"""
        if name in self.jobs:
            try:
                job = self.scheduler.get_job(self.jobs[name])
                if job:
                    # Создаем новый триггер
                    new_trigger = CronTrigger(**time_dict)
                    job.reschedule(new_trigger)
                    log.info(f'Задача {name} обновлена: {time_dict}')
                    return True
            except Exception as e:
                log.error(f'Ошибка обновления задачи {name}: {e}')
        return False