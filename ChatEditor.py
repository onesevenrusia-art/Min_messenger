import psycopg2
import time

def create_chat_database():
    """Создаем базу и таблицы для чата"""
    
    try:
        # Сначала подключаемся к стандартной БД postgres
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="123456",  # твой пароль!
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Создаем базу для чата (если еще не существует)
        cursor.execute("CREATE DATABASE IF NOT EXISTS chat_app")
        print("✅ База chat_app создана/уже существует")
        
        cursor.close()
        conn.close()
        
        # Ждем немного чтобы БД инициализировалась
        print("⏳ Ждем инициализации базы...")
        time.sleep(2)
        
        # Теперь подключаемся к нашей новой базе
        conn = psycopg2.connect(
            host="localhost",
            database="chat_app",  # наша база!
            user="postgres",
            password="qwerty",    # твой пароль!
            port="5432"
        )
        cursor = conn.cursor()
        
        print("✅ Успешно подключились к chat_app!")
        
        # Создаем таблицы
        tables_sql = [
            # Таблица пользователей
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # Таблица чатов
            """
            CREATE TABLE IF NOT EXISTS chats (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,
            # Таблица сообщений
            """
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                page_number INTEGER DEFAULT 1
            )
            """
        ]
        
        for i, table_sql in enumerate(tables_sql):
            cursor.execute(table_sql)
            table_names = ["users", "chats", "messages"]
            print(f"✅ Таблица {table_names[i]} создана")
        
        # Добавляем тестовые данные (если их нет)
        cursor.execute("""
            INSERT INTO users (username) VALUES 
            ('user1'), ('user2'), ('user3')
            ON CONFLICT (username) DO NOTHING
        """)
        
        cursor.execute("""
            INSERT INTO chats (name) VALUES 
            ('Общий чат')
            ON CONFLICT DO NOTHING
        """)
        
        # Проверяем есть ли сообщения
        cursor.execute("SELECT COUNT(*) FROM messages")
        message_count = cursor.fetchone()[0]
        
        if message_count == 0:
            # Добавляем тестовые сообщения
            for i in range(1, 151):
                user_id = (i % 3) + 1  # чередуем пользователей
                page_number = ((i - 1) // 100) + 1  # вычисляем пачку
                
                cursor.execute("""
                    INSERT INTO messages (chat_id, user_id, message_text, page_number)
                    VALUES (%s, %s, %s, %s)
                """, (1, user_id, f"Тестовое сообщение {i}", page_number))
            
            print("✅ Добавлено 150 тестовых сообщений")
        else:
            print(f"✅ В базе уже есть {message_count} сообщений")
        
        conn.commit()
        
        # Показываем статистику
        print("\n📊 Статистика базы:")
        cursor.execute("SELECT COUNT(*) FROM users")
        print(f"   Пользователей: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM chats")
        print(f"   Чатов: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        print(f"   Сообщений: {cursor.fetchone()[0]}")
        
        print("\n📦 Пачки сообщений:")
        cursor.execute("""
            SELECT page_number, COUNT(*) 
            FROM messages 
            GROUP BY page_number 
            ORDER BY page_number
        """)
        for page_num, count in cursor.fetchall():
            print(f"   Пачка {page_num}: {count} сообщений")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 База данных готова к работе!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Проверь пароль PostgreSQL")
        print("2. Убедись что служба PostgreSQL запущена")
        print("3. Попробуй перезапустить PostgreSQL")

if __name__ == "__main__":
    create_chat_database()