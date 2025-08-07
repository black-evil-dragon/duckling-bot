# 📅 Duckling - телеграм-бот

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-22.0-orange)](https://github.com/python-telegram-bot/python-telegram-bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data Source](https://img.shields.io/badge/Data_Source-tt2.vogu35.ru-green)](https://tt2.vogu35.ru/)

### Бот для удобного просмотра расписания Вологодского государственного университета
* 💻 **Основной разработчик**: [Semyon Golgan](https://github.com/black-evil-dragon)  
* 💬 **Telegram**: https://t.me/duckling_schedule_bot

```python
from imeikn import Student

# Для ИМЕиКН с любовью
me = Student()
me.sendLove()
```

   
## 🌟 Возможности
   - Получение расписания для своей группы на 3 недели вперед
   - Удобный выбор группы (по курсам и названиям)
   - Автоматическое определение текущей недели
   - Поддержка нескольких институтов ВоГУ
   <!-- - Автоматическое обновление данных при изменении расписания   -->
   <!-- - Уведомления о изменениях (в разработке)   -->


## 🤝 Как помочь проекту
Мы рады вкладу от сообщества!
**Как помочь:**
* Форкните репозиторий
* Создайте ветку с вашими изменениями (git checkout -b feature/amazing-feature)
* Сделайте коммит (git commit -m 'Add some amazing feature')
* Запушьте в форк (git push origin feature/amazing-feature)
* Откройте Pull Request


## 🛠 Установка

### 1. Клонируйте репозиторий:
```bash
git clone https://github.com/black-evil-dragon/duckling-bot.git
cd duckling-bot
```

### 2. Активируйте виртуальную среду:
```bash
python3.12 -m venv ./venv # py -3.12 -m venv ./venv
```

### 3. Добавьте переменные окружения и проверьте файл конфигурации
```python
# ./core/settings/config.py
from dotenv import dotenv_values

config = dotenv_values('.env')

BOT_TOKEN=config.get('BOT_TOKEN')
DB_FILEPATH=config.get('DB_FILEPATH')

API_ID=config.get('API_ID')
API_KEY=config.get('API_KEY')
API_URL = config.get('API_URL')

```

### 4. Запустите бота
```bash
python main.py
```

## ⚖️ Правовые аспекты

1. **Источник данных**:  
   Бот получает информацию исключительно из публично доступного расписания на [официальном сайте ВоГУ](https://tt2.vogu35.ru/)

2. **Ответственность**:  
   Разработчик не несет ответственности за:  
   - Точность предоставляемых данных
   - Изменения в работе API университета
      > Реализованны алгоритмы API не прошли проверку временем и аналогично боту нуждаются в документировании, рефакторинге и прочему.
   - Временную недоступность сервиса

## 📜 Лицензия
Этот проект распространяется под лицензией MIT.
При использовании кода просьба указывать оригинального автора.

```bash
MIT License
Copyright (c) 2025 Semyon Golgan
```
