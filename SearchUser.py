from sqlalchemy import create_engine, Column, String, Boolean, Text, CheckConstraint, Integer, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

engine = create_engine('sqlite:///Users.db')
Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'
    
    email = Column(String(255), primary_key=True)
    userid = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    about = Column(Text(1024))
    photo = Column(String(255))
    blocked = Column(Boolean, default=False)
    token = Column(String(500))
    chats = Column(Text)
    
    __table_args__ = (
        CheckConstraint('LENGTH(about) <= 1024', name='about_length_check'),
    )
    
    def set_chats(self, chats_list):
        self.chats = json.dumps(chats_list)
    
    def get_chats(self):
        return json.loads(self.chats) if self.chats else []
    
    def __repr__(self):
        data = {
            "email": self.email,
            "userid": self.userid,
            "name": self.name,
            "phone": self.phone,
            "blocked": self.blocked
        }
        return json.dumps(data, ensure_ascii=False)

# Создаем таблицу
Base.metadata.create_all(engine)

class UserManager:
    def __init__(self, database_url='sqlite:///Users.db'):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def _user_to_dict(self, user):
        """Конвертирует объект User в словарь"""
        if not user:
            return None
        return {
            "email": user.email,
            "userid": user.userid,
            "name": user.name,
            "phone": user.phone,
            "about": user.about,
            "photo": user.photo,
            "blocked": user.blocked,
            "token": user.token,
            "chats": user.get_chats() if user.chats else []
        }
    
    def get_user_by_id(self, userid):
        """Найти пользователя по ID и вернуть dict"""
        session = self.Session()
        try:
            user = session.query(User).filter(User.userid == userid).first()
            return self._user_to_dict(user) or {}
        finally:
            session.close()
    
    def get_user_by_email(self, email):
        """Найти пользователя по email и вернуть dict"""
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            return self._user_to_dict(user) or {}
        finally:
            session.close()
    
    def get_all_users(self):
        """Получить всех пользователей как list of dict"""
        session = self.Session()
        try:
            users = session.query(User).all()
            return [self._user_to_dict(user) for user in users]
        finally:
            session.close()
    
    def search_users_by(self, name_pattern, by="name"):
        """Поиск пользователей по имени, возвращает list of dict"""
        session = self.Session()
        try:
            match by:
                case "name":users = session.query(User).filter(
                User.name.ilike(f'%{name_pattern}%')
            ).all()
                case "email":users = session.query(User).filter(
                User.email.ilike(f'%{name_pattern}%')
            ).all()
                case "phone":users = session.query(User).filter(
                User.phone.ilike(f'%{name_pattern}%')
            ).all()
                case "id": users = session.query(User).filter(
                User.userid.ilike(f'%{name_pattern}%')
            ).all()
            return [self._user_to_dict(user) for user in users]
        finally:
            session.close()
    
    def search_users_by_phone(self, phone_pattern):
        """Поиск пользователей по телефону, возвращает list of dict"""
        session = self.Session()
        try:
            users = session.query(User).filter(
                User.phone.ilike(f'%{phone_pattern}%')
            ).all()
            return [self._user_to_dict(user) for user in users]
        finally:
            session.close()
    
    def get_active_users(self):
        """Получить активных пользователей как list of dict"""
        session = self.Session()
        try:
            users = session.query(User).filter(User.blocked == False).all()
            return [self._user_to_dict(user) for user in users]
        finally:
            session.close()
    
    def get_blocked_users(self):
        """Получить заблокированных пользователей как list of dict"""
        session = self.Session()
        try:
            users = session.query(User).filter(User.blocked == True).all()
            return [self._user_to_dict(user) for user in users]
        finally:
            session.close()
    
    def add_user(self, email, userid, name, phone=None, about=None, photo=None, 
                blocked=False, token=None, chats=None):
        """Добавить пользователя и вернуть dict созданного пользователя"""
        session = self.Session()
        try:
            # Проверяем существование
            if session.query(User).filter(User.email == email).first():
                return {"error": f"Пользователь с email {email} уже существует"}
            
            if session.query(User).filter(User.userid == userid).first():
                return {"error": f"Пользователь с ID {userid} уже существует"}
            
            # Создаем пользователя
            new_user = User(
                email=email,
                userid=userid,
                name=name,
                phone=phone,
                about=about,
                photo=photo,
                blocked=blocked,
                token=token
            )
            
            if chats:
                new_user.set_chats(chats)
            
            session.add(new_user)
            session.commit()
            
            return self._user_to_dict(new_user)
            
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()
    
    def update_user(self, email, **kwargs):
        """Обновить пользователя и вернуть dict обновленного"""
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return {"error": f"Пользователь с email {email} не найден"}
            
            # Обновляем поля
            allowed_fields = ['name', 'phone', 'about', 'photo', 'blocked', 'token']
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            if 'chats' in kwargs:
                user.set_chats(kwargs['chats'])
            
            session.commit()
            return self._user_to_dict(user)
            
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()
    
    def delete_user(self, email):
        """Удалить пользователя и вернуть dict со статусом"""
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return {"error": f"Пользователь с email {email} не найден"}
            
            user_data = self._user_to_dict(user)  # сохраняем данные перед удалением
            
            session.delete(user)
            session.commit()
            
            return {
                "success": True, 
                "message": f"Пользователь {email} удален",
                "deleted_user": user_data
            }
            
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()
    
    def user_exists(self, email=None, userid=None):
        """Проверить существование пользователя, вернуть dict"""
        session = self.Session()
        try:
            query = session.query(User)
            
            if email:
                query = query.filter(User.email == email)
            if userid:
                query = query.filter(User.userid == userid)
            
            exists = query.first() is not None
            
            return {
                "exists": exists,
                "email": email,
                "userid": userid
            }
        finally:
            session.close()

    def get_max_userid(self):
        """Получить максимальный userid из базы, вернуть dict"""
        session = self.Session()
        try:
            max_id = session.query(func.max(User.userid)).scalar()
            return {
                "id": max_id if max_id is not None else 0,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
        finally:
            session.close()
    
    

#db = UserManager()
#db.add_user("onesevenrusia@gmail.com",0,"Alex","79157683304")
#
#print(db.get_all_users())
#print(db.get_user_by_id(0))