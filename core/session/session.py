import requests
import logging
import os
from requests.exceptions import RequestException

# Настройка логирования
log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)

class Session:
    session: 'requests.Session' = None
    token: str = None

    URL = "https://tt2.vogu35.ru/"
    TOKEN_FILE = "csrf_token.txt"

    def __init__(self):
        try:
            log.info("Инициализация новой сессии")
            self.session = requests.Session()
            
            self.session.headers = { 
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10 10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.8.2171.95 Safari/537.36", 
                "Accept": "application/json", 
                "X-Requested-With": "XMLHttpRequest", 
            }
            
            if self.load_token_from_file():
                log.debug("-\tCSRF токен загружен из файла")
            else:
                log.debug("-\tПопытка получения CSRF токена с сервера")
                self.get_crft_token(self.URL)
                self.save_token_to_file()
            
            self.update_session_headers()
            log.info("-\tСессия успешно инициализирована")
            
        except Exception as error:
            log.critical(f"!\tКритическая ошибка при инициализации сессии: {str(error)}")
            raise RuntimeError(f"Не удалось инициализировать сессию: {str(error)}")

    def update_session_headers(self):
        self.session.headers.update({
            "X-CSRFToken": self.token,
        })

    def load_token_from_file(self) -> bool:
        if not os.path.exists(self.TOKEN_FILE): return False
            
        try:
            with open(self.TOKEN_FILE, "r") as f:
                token = f.read().strip()
                if token:
                    self.token = token
                    return True
            return False

        except Exception as e:
            log.warning(f"Не удалось прочитать токен из файла: {str(e)}")
            return False

    def save_token_to_file(self) -> None:
        if not self.token: return
            
        try:
            with open(self.TOKEN_FILE, "w") as f:
                f.write(self.token)
            log.debug(f"-\tCSRF токен сохранен в файл {self.TOKEN_FILE}")
        except Exception as e:
            log.warning(f"Не удалось сохранить токен в файл: {str(e)}")

    def get_crft_token(self, url) -> str:
        try:
            log.debug(f"-\t- Запрос CSRF токена по URL: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            log.debug("-\tПроверка заголовков ответа для извлечения токена")
            set_cookie_header = response.headers.get("Set-Cookie")
            
            if not set_cookie_header:
                error_msg = "Заголовок Set-Cookie отсутствует в ответе"
                log.error(error_msg)
                raise ValueError(error_msg)
                
            try:
                token = set_cookie_header.split("=")[1].split(";")[0]
                if not token: 
                    raise ValueError("Пустой токен")
                    
                self.token = token
                log.debug(f"-\t- Успешно получен CSRF токен: {token[:5]}...")
                return token
                
            except Exception as error:
                error_msg = f"Не удалось извлечь токен из заголовка Set-Cookie: {set_cookie_header}"
                log.error(error_msg)
                raise error
                
        except RequestException as error:
            error_msg = f"Ошибка сети при запросе CSRF токена: {str(error)}"
            log.error(error_msg)
            raise error

        except Exception as error:
            error_msg = f"Неожиданная ошибка при получении CSRF токена: {str(error)}"
            log.error(error_msg)
            raise error

    def post(self, url, data=None, json=None, **kwargs):
        try:
            response = self.session.post(url, data=data, json=json, **kwargs)
            
            if response.status_code == 403:
                log.warning("-\tПолучен статус 403, пробуем обновить CSRF токен")
                self.get_crft_token(self.URL)
                self.save_token_to_file()
                self.update_session_headers()
                
                response = self.session.post(url, data=data, json=json, **kwargs)
                
            return response
            
        except Exception as error:
            log.error(f"Ошибка при выполнении POST-запроса: {str(error)}")
            raise