from sqlite3 import Error

import sqlite3


#* Other packages ________________________________________________________________________
from typing import Optional, Any, List, Dict, Tuple

import logging




log = logging.getLogger("duckling")
log.setLevel(logging.DEBUG)


class Database:

    filename: str = "bot.db"

    def __init__(self, filename: str = None):

        if self.filename:
            self.filename = filename

        self.connection = None
        
        self.create_tables()

    def __del__(self):
        self.close_connection()



    # * __________________________________________________________
    # * |               Connection management                       |
    def create_connection(self) -> Optional[sqlite3.Connection]:
        try:
            conn = sqlite3.connect(
                self.filename, 
                check_same_thread=False
            )

            log.info(f"Успешное подключение к SQLite DB {self.filename}")
            return conn

        except Error as e:
            log.error(f"Ошибка подключения к SQLite DB: {e}")
        return None
    
    def get_connection(self) -> sqlite3.Connection:
        if self.connection is None:
            self.connection = self.create_connection()
    
        return self.connection
    
    def close_connection(self) -> None:
        if self.connection:
            self.connection.close()
            self.connection = None
            log.info("Соединение с SQLite DB закрыто")
    # * |____________________________________________________________|




    # * ____________________________________________________________
    #* |               Executing SQL queries                         |
    def execute_query(self, query: str, params: tuple = (), commit: bool = False) -> Optional[sqlite3.Cursor]:

        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            return cursor
        except Error as e:
            log.error(f"Ошибка выполнения запроса: {query}. Ошибка: {e}")
            return None
    # * |____________________________________________________________|




    # * ______________________________________________________________
    # * |               Creating tables                               |
    def create_tables(self) -> None:
        """Создаёт таблицу users, если её нет."""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            is_bot BOOLEAN,

            first_name TEXT NOT NULL,
            last_name TEXT,
            username TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            group_id INTEGER,
            subgroup_id INTEGER
        );
        """
        self.execute_query(query, commit=True)
        
        # ! TEMP
        # try:
        #     self.execute_query("ALTER TABLE users ADD COLUMN group_id INTEGER;", commit=True)
        # except Exception as e:
        #     log.debug(f"Колонка group_id уже существует: {e}")
        
        # try:
        #     self.execute_query("ALTER TABLE users ADD COLUMN subgroup_id INTEGER;", commit=True)
        # except Exception as e:
        #     log.debug(f"Колонка subgroup_id уже существует: {e}")
        

        log.info("Таблица users создана/обновлена")
    # * |____________________________________________________________|




    # * ______________________________________________________________
    # * |                   User management                          |
    def add_or_update_user(self, user_data: Dict[str, Any]) -> bool:
        query = """
            INSERT INTO users (
                user_id, is_bot, first_name, last_name, username,
                group_id, subgroup_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                username = excluded.username,
                group_id = CASE 
                    WHEN excluded.group_id IS NOT NULL AND excluded.group_id != '' 
                    THEN excluded.group_id 
                    ELSE users.group_id 
                END,
                subgroup_id = CASE 
                    WHEN excluded.subgroup_id IS NOT NULL AND excluded.subgroup_id != '' 
                    THEN excluded.subgroup_id 
                    ELSE users.subgroup_id 
                END
        """

        params = (
            user_data.get("id"),
            user_data.get("is_bot", False),
            user_data.get("first_name", ""),
            user_data.get("last_name", ""),
            user_data.get("username"),
            user_data.get("group_id"),
            user_data.get("subgroup_id")
        )
        
        
        try:
            cursor = self.execute_query(query, params, commit=True)

            return cursor is not None
        except Exception as e:
            log.error(f"Ошибка обновления пользователя {user_data.get('id')}: {e}")
            return False
    

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE user_id = ?"
        cursor = self.execute_query(query, (user_id,))

        if cursor:
            row = cursor.fetchone()
            if row:
                columns = ["user_id", "is_bot", "first_name", "last_name", "username", "created_at", "group_id", "subgroup_id",]
                return dict(zip(columns, row))
        return None
    # * |____________________________________________________________|