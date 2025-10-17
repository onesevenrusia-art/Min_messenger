import sqlite3
from contextlib import contextmanager

class ChatDataBase:
    def __init__(self, useremailID):
        self.tablename=useremailID
        self.conn = sqlite3.connect(f"databases/UserChats/{useremailID}ChatsDatabase.db", 
            check_same_thread=False  # ← ЭТА СТРОЧКА РЕШАЕТ ПРОБЛЕМУ
            )
        self.cursor = self.conn.cursor()
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.tablename} (
                id int PRIMARY KEY NOT NULL,
            )
            ''')
        self.conn.commit()

    @contextmanager
    def _get_cursor(self):
        """Context manager для автоматического управления курсором"""
        try:
            yield self.cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def GetChats(self):
        with self._get_cursor():
            self.cursor.execute(f"SELECT * FROM {self.tablename}")
            info = self.cursor.fetchall()
            return info

    def DeleteUserFromChat(self, chatid):
        with self._get_cursor():
            self.cursor.execute(f"DELETE FROM {self.tablename} WHERE id = ?", (chatid,))

    def close(self):
        """Закрыть соединение с базой данных"""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Деструктор - автоматически закрывает соединение при удалении объекта"""
        self.close()