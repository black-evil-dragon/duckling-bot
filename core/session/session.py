from dotenv import dotenv_values

import requests
import logging

from core.settings import config
from core.session.decorators import try_repeat_catch
from core.data.group import Group



# Настройка логирования
log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)



class Session:
    session: 'requests.Session' = None

    URL = config.API_URL


    def __init__(self, id: int, key: str, refresh_token: str = None):
        try:
            log.info("Инициализация новой сессии")
            self.session = requests.Session()
            
            self.session.headers = { 
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10 10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.8.2171.95 Safari/537.36", 
                "Accept": "application/json", 
                "X-Requested-With": "XMLHttpRequest", 
            }

            self.auth_data = dict(
                id=id,
                key=key,
                refresh_token=refresh_token or dotenv_values("tokens.env").get('REFRESH_TOKEN'),
            )

            self.touch()


            if self.auth_data.get('refresh_token') is None:
                log.info('-\t| Токены отсутствуют')
                self.create_session()

            else:
                self.check_session(is_first=True)
            
            log.info("+\tСессия успешно инициализирована")


            self.get_all_groups()

            
        except Exception as error:
            log.critical(f"!\tКритическая ошибка при инициализации сессии: {str(error)}")
            raise RuntimeError(f"Не удалось инициализировать сессию: {str(error)}")
        
    # * |___________________________________________________________      




    # * ____________________________________________________________
    # * |                       Update data                          
    def get_all_groups(self):
        path = 'group/get-tree/'

        response: 'requests.Response' = self.post(path)
        
        
        response_data: dict = response.json()

        group_ids = {}
        for institute in response_data.get('institutes', []):
            name = institute.get('name')
            group_ids[name] = {i: {} for i in range(1, len(institute.get('courses', [])) + 1)}

            for course in institute.get('courses', []):
                course['groups'].sort(key=lambda group: group.get('name'))

                for group in course.get('groups', []):
                    group_ids[name][course.get('course')].update({
                        group.get('name'): str(group.get('id'))
                    })

        Group.save_to_json(group_ids)

    # * |___________________________________________________________




    # * ____________________________________________________________
    # * |                 Http methods                      
    @try_repeat_catch(
        max_attempts=2,
        delay_seconds=2.0,
    )             
    def post(self, path, data=None, json=None, **kwargs) -> 'requests.Response':
        url = f'{self.URL}/{path}'
        response = self.session.post(url, data=data, json=json, **kwargs)
        # log.debug(f'POST {path} - {response.status_code}')
        
        if response.status_code in [400, 403]:
            log.warning(f"\tПолучен статус {response.status_code}, повторяем авторизацию")

            self.check_session()

            response = self.session.post(url, data=data, json=json, **kwargs)

        elif response.status_code in [500]:
            log.error(f"\tПолучен статус {response.status_code}, ошибка в работе сервера")

            if response.json().get('error', ""):
                log.error(response.json().get('error', ""))

            response.raise_for_status()
            
        return response
    # * |___________________________________________________________




    # * ____________________________________________________________
    # * |               Tokens utils                                
    def set_tokens(self, response: 'requests.Response'):
        try:
            data: dict = response.json()

            self.auth_data.update(dict(
                access_token=data.get('access'),
                refresh_token=data.get('refresh'),
            ))

            self.session.headers.update({
                'Authorization': f"Bearer {data.get('access')}"
            })

            with open("tokens.env", "w") as f:
                f.write(f"REFRESH_TOKEN={self.auth_data['refresh_token']}")


        except Exception as error:
            raise Exception(f"Не удалось установить токены авторизации. {error}")
        
    def set_csrf(self, response: 'requests.Response'):
        self.session.headers.update({
            "X-CSRFToken": response.cookies.get('csrftoken'),
        })
    # * |___________________________________________________________




    # * ____________________________________________________________
    # * |                       Session utils                
    def touch(self):
        path = f'{self.URL}/auth/'

        log.info('\t| Установка соединения')

        # - Получение csrf токена
        response = self.session.get(path, params=dict(
            id=self.auth_data.get("id"),
        ))

        if response.json().get('success', False):
            self.set_csrf(response)
        else:
            log.error("Не удалось получить csrf токен")
            raise RuntimeError('Неудачная попытка авторизации. ID подключения отсутствует!')
        


    def create_session(self):
        path = f'{self.URL}/auth/'

        log.info('\t| Авторизуемся по id и key')

        #* - Авторизация соединения
        response = self.session.post(path, json=dict(
            id=self.auth_data.get("id"),
            key=self.auth_data.get("key"),
        ))


        if response.json().get('success', False):
            self.set_tokens(response)
        else:
            raise Exception("Не удалось авторизоваться на сервере")      



    def check_session(self, is_first=False):
        path = f'{self.URL}/auth-check/'

        log.info('\t| Проверяем актуальность токенов авторизации')

        if is_first: return self.update_tokens()
            

        response = self.session.get(path)

        if response.json().get('success', False):
            log.info('\t| Успешно!')

        else:
            self.update_tokens()
            

 
    def update_tokens(self):
        path = f'{self.URL}/auth-update/'

        log.info('\t| Обновление токенов через refresh-токен')

        self.session.headers.update({
            'Authorization': f"Bearer {self.auth_data.get('refresh_token')}"
        })

        response = self.session.get(path)

        if response.json().get('success', False):
            self.set_tokens(response)
            log.info('\t| Успешно!')

        else:
            log.info('\t| Ошибка проверки токенов. Пробуем авторизоваться через id и key')
            self.create_session()
    # * |___________________________________________________________

