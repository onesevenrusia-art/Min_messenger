import sqlite3
from contextlib import contextmanager

class ChatDataBase:
    def __init__(self):
        self.conn = sqlite3.connect("databases/ChatssDatabase.db", 
            check_same_thread=False  # ← ЭТА СТРОЧКА РЕШАЕТ ПРОБЛЕМУ
            )
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Chats (
                id int PRIMARY KEY NOT NULL,
                users TEXT NOT NULL,
                name TEXT NOT NULL,
                about TEXT,
                photo BLOB,
                info TEXT 
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

        
    def getChat(self, chatid, data=list):
        with self._get_cursor():
            self.cursor.execute(f"SELECT {', '.join(data)} FROM Chats WHERE id = ?", (chatid,))
            info = self.cursor.fetchone()
            return info

    def UpdateData(self, id, users=None, name=None, about=None, photo=None, info=None):
        with self._get_cursor():
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if users is not None:
                updates.append("users = ?")
                params.append(users)
            if about is not None:
                updates.append("about = ?")
                params.append(about)
            if photo is not None:
                updates.append("photo = ?")
                params.append(photo)
            if info is not None:
                updates.append("info = ?")
                params.append(info)
            if not updates:
                print("❌ Нет данных для обновления")
                return False

            sql = f"UPDATE Chats SET {', '.join(updates)} WHERE id = ?"
            
            try:
                self.cursor.execute(sql, params)
                return True
            except Exception as e:
                print(f"❌ Ошибка обновления: {e}")
                return False



    def deleteChat(self, chatid):
        with self._get_cursor():
            self.cursor.execute("DELETE FROM Chats WHERE id = ?", (chatid,))

    def close(self):
        """Закрыть соединение с базой данных"""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Деструктор - автоматически закрывает соединение при удалении объекта"""
        self.close()