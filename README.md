# 📅 Duckling - телеграм-бот

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-22.0-orange)](https://github.com/python-telegram-bot/python-telegram-bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Data Source](https://img.shields.io/badge/Data_Source-tt2.vogu35.ru-green)](https://tt2.vogu35.ru/)

* Бот для удобного просмотра расписания Вологодского государственного университета.  
* **Основной разработчик**: [Semyon Golgan](https://github.com/black-evil-dragon)  
* https://t.me/duckling_schedule_bot

## For **ИМЕиКН** with love


## ⚖️ Правовые аспекты

1. **Источник данных**:  
   Бот получает информацию исключительно из публично доступного расписания на [официальном сайте ВоГУ](https://tt2.vogu35.ru/).

2. **Частота запросов**:  
   Для избежания нагрузки на серверы университета реализованы:
   ***(TODO)***

3. **Рекомендации**:  
   При использовании бота в production-режиме рекомендуется:
   - Указывать источник данных в интерфейсе бота
   ***(TODO)***

## 🌟 Возможности
- Получение расписания для своей группы на 3 недели вперед
- Удобный выбор группы (по курсам и названиям)
- Автоматическое определение текущей недели

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
python3.10 -m venv ./venv # py -3.10 -m venv ./venv
```

### 3. Создайте файл конфигурации
```python
# ./utils/config.py
TOKEN="TOKEN"
```

### 4. Запустите бота
```bash
python main.py
```

## 🚀 Как использовать
### Основные команды:

* #### /set_group - Выбрать свою группу
* #### /schedule - Получить расписание

## 📜 Лицензия
Этот проект распространяется под лицензией MIT.
При использовании кода просьба указывать оригинального автора.

```bash
MIT License
Copyright (c) 2025 Semyon Golgan
```
