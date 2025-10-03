import sqlite3
from contextlib import contextmanager

class usersDataBase:
    def __init__(self):
        self.conn = sqlite3.connect("databases/UsersDatabase.db", 
            check_same_thread=False  # ← ЭТА СТРОЧКА РЕШАЕТ ПРОБЛЕМУ
            )
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                email TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                about TEXT,
                photo BLOB,
                block INTEGER DEFAULT 0,
                token TEXT NOT NULL,
                chats TEXT NOT NULL
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

    def adduser(self, email, name, token, phone="none", about="none", photo=0b0, block=False, chats="[]"):
        with self._get_cursor():
            try:
                self.cursor.execute(
                    "INSERT INTO Users (email, name, phone, about, photo, block, token, chats) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                    (email, name, phone, about, photo, int(block), token, chats)
                )
            except sqlite3.IntegrityError:
                return 
        
    def getUser(self, email, data=list):
        with self._get_cursor():
            self.cursor.execute(f"SELECT {', '.join(data)} FROM Users WHERE email = ?", (email,))
            info = self.cursor.fetchone()
            return info

    def UpdateData(self, email, name=None, phone=None, about=None, photo=None, token=None, chats=None):
        with self._get_cursor():
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if phone is not None:
                updates.append("phone = ?")
                params.append(phone)
            if about is not None:
                updates.append("about = ?")
                params.append(about)
            if photo is not None:
                updates.append("photo = ?")
                params.append(photo)
            if token is not None:
                updates.append("token = ?")
                params.append(token)
            if chats is not None:
                updates.append("chats = ?")
                params.append(chats)    
            if not updates:
                print("❌ Нет данных для обновления")
                return False
            
            params.append(email)
            sql = f"UPDATE Users SET {', '.join(updates)} WHERE email = ?"
            
            try:
                self.cursor.execute(sql, params)
                return True
            except Exception as e:
                print(f"❌ Ошибка обновления: {e}")
                return False

    def allUsers(self):
        with self._get_cursor():
            self.cursor.execute("SELECT * FROM Users")
            info = self.cursor.fetchall()
            return info

    def deleteUser(self, email):
        with self._get_cursor():
            self.cursor.execute("DELETE FROM Users WHERE email = ?", (email,))

    def close(self):
        """Закрыть соединение с базой данных"""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Деструктор - автоматически закрывает соединение при удалении объекта"""
        self.close()