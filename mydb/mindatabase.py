from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import json

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    about = Column(Text)
    photo = Column(String(255))
    blocked = Column(DateTime, default=None)
    devices = Column(Text, default="{}")
    chats = Column(Text, default="[]")
    
    messages = relationship("Message", back_populates="user")

    def get_devices(self):
        return json.loads(self.devices or "{}")
    
    def set_devices(self, devices_dict):
        self.devices = json.dumps(devices_dict)
    
    def get_chats(self):
        return json.loads(self.chats or "[]")
    
    def set_chats(self, chats_list):
        self.chats = json.dumps(chats_list)

class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    participants = Column(Text, default="[]")
    about = Column(Text)
    photo = Column(String(255))
    created = Column(DateTime, default=datetime.now())
    
    messages = relationship("Message", back_populates="chat")
    
    def get_participants(self):
        return json.loads(self.participants or "[]")
    
    def set_participants(self, participants_list):
        self.participants = json.dumps(participants_list)

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    internal_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    datatype = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.now())
    
    chat = relationship("Chat", back_populates="messages")
    user = relationship("User", back_populates="messages")


class DataBaseManager:
    def __init__(self, database_url='sqlite:///Databases/Main.db'):
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _user_to_dict(self, user):
        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "about": user.about,
            "photo": user.photo,
            "blocked": user.blocked,
            "devices": user.get_devices(),
            "chats": user.get_chats()
        }
    
    def add_user(self, email, name, phone=None, about=None, photo=None, blocked=None, devices=None, chats=None):
        session = self.Session()
        try:
            if session.query(User).filter(User.email == email).first():
                return {"error": "Пользователь с таким email уже существует"}
            r=self.get_max_objectid(User)
            if r["success"]:r=r["id"]+1
            user = User(id=r,email=email, name=name, phone=phone, about=about, photo=photo, blocked=blocked)
            if devices:
                user.set_devices(devices)
            if chats:
                user.set_chats(chats)
            session.add(user)
            session.commit()
            return self._user_to_dict(user)
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()

    def update_user(self, email, **kwargs):
        """['name', 'phone', 'about', 'photo', 'blocked', 'devices']"""
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return {"error": f"Пользователь с email {email} не найден"}
            allowed_fields = ['name', 'phone', 'about', 'photo', 'blocked', 'devices']
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, str(value))
            session.commit()
            return self._user_to_dict(user)
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()

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
            users = session.query(User).filter(User.blocked == None).all()
            return [self._user_to_dict(user) for user in users]
        finally:
            session.close()
    
    def get_blocked_users(self):
        """Получить заблокированных пользователей как list of dict"""
        session = self.Session()
        try:
            users = session.query(User).filter(User.blocked != None).all()
            return [self._user_to_dict(user) for user in users]
        finally:
            session.close()

    def delete_user(self, email):
        """Удалить пользователя и вернуть dict со статусом"""
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return {"error": f"Пользователь с email {email} не найден"}
            session.delete(user)
            session.commit()
            return {
                "success": True
            }
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()

    def is_user_blocked(self, email):
        """Проверить заблокирован ли пользователь"""
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user or not user.blocked:
                return False
            if user.blocked < datetime.utcnow():
                user.blocked = None
                session.commit()
                return False
            
            return True
        finally:
            session.close()

    def block_user(self, email, hours=24):
        """Заблокировать пользователя на N часов"""
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return {"error": "Пользователь не найден"}
            user.blocked = datetime.now() + timedelta(hours=hours)
            session.commit()
            
            return {
                "success": True,
                "message": f"Пользователь заблокирован до {user.blocked}",
                "blocked_until": user.blocked
            }
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()
            
    def add_device(self,email,devicename,devicedata):
        session = self.Session()
        device = self.get_user_by_email(email)
        if len(device)>0:
            device=device["devices"]
            device[devicename]=devicedata
            self.update_user(email=email,devices=device)
        else:
            raise ValueError("not find user")
        session.commit()

    def add_chat(self, name, participants=[], about=None, photo=None):
        session = self.Session()
        try:
            r=self.get_max_objectid(Chat)
            if r["success"]:r=r["id"]+1
            chat = Chat(id=r, name=name, about=about, photo=photo)
            if participants:
                chat.set_participants(participants)
            session.add(chat)
            session.commit()
            return {"success": True, "chat_id": chat.id}
        finally:
            session.close()

    def update_chat(self, id, **kwargs):
        """['name', 'participants', 'about', 'photo']"""
        session = self.Session()
        try:
            chat = session.query(Chat).filter(Chat.id == id).first()
            if not chat:
                return {"error":"id не найден"}
            allowed_fields = ['name', 'participants', 'about', 'photo']
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(chat, field):
                    setattr(chat, field, str(value))
            session.commit()
            return self._user_to_dict(chat)
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()

    def get_chat(self, chat_id):
        session = self.Session()
        try:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            if not chat:
                return None
            return {
                "id": chat.id,
                "name": chat.name,
                "participants": chat.get_participants(),
                "about": chat.about,
                "photo": chat.photo,
                "created": chat.created
            }
        finally:
            session.close()

    def add_message(self, chat_id, user_id, datatype, content, created=None):
        session = self.Session()
        try:
            r=self.get_max_objectid(Message)
            if r["success"]:r=r["id"]+1
            last_seq = session.query(func.max(Message.seq)).filter(Message.chat_id == chat_id).scalar()
            if type(last_seq) != int: return
            msg = Message(id=r, chat_id=chat_id, user_id=user_id, internal_id=last_seq+1, datatype=datatype, content=content, created=created)
            session.add(msg)
            session.commit()
            return {"success": True, "message_id": msg.id}
        finally:
            session.close()

    def update_message(self, chat_id, chat_message_id, new_content,datatype):
        session = self.Session()
        try:
            msg = session.query(Message).filter(
                Message.chat_id == chat_id,
                Message.internal_id == chat_message_id
            ).first()

            if not msg:
                return {"error": "Сообщение не найдено"}

            msg.content = new_content
            msg.datatype = datatype
            session.commit()

            return {
                "success": True,
                "chat_id": chat_id,
                "chat_message_id": chat_message_id,
                "content": msg.content,
                "datatype": msg.datatype
            }
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()

    def delete_message(self, chat_id, internal_id):
        session = self.Session()
        try:
            msg = session.query(Message).filter(
                Message.chat_id == chat_id,
                Message.internal_id == internal_id
            ).first()

            if not msg:
                return {"error": "Сообщение не найдено"}

            session.delete(msg)
            session.commit()

            return {
                "success": True,
                "chat_id": chat_id,
                "internal_id": internal_id
            }
        finally:
            session.close()

    def delete_chat(self,chat_id):
        session = self.Session()
        try:
            chat = session.query(Chat).filter(Chat.id == chat_id).first()
            if not chat:
                return {"error": f"id не найден"}
            session.delete(chat)
            session.commit()
            return {
                "success": True
            }
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()

    def get_max_objectid(self, obj=User):
        session = self.Session()
        try:
            max_id = session.query(func.max(obj.id)).scalar()
            return {
                "id": max_id if max_id is not None else 0,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}
        finally:
            session.close()

    
