from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import json

Base = declarative_base()

# ---------------------- МОДЕЛИ ----------------------
class User(Base):
    tablename = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    about = Column(Text)
    photo = Column(String(255))
    blocked = Column(DateTime, default=None)
    devices = Column(Text, default="{}")  # JSON
    chats = Column(Text, default="[]")    # JSON список ID чатов
    
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
    tablename = 'chats'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    participants = Column(Text, default="[]")  # JSON список user.id
    about = Column(Text)
    photo = Column(String(255))
    created = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="chat")
    
    def get_participants(self):
        return json.loads(self.participants or "[]")
    
    def set_participants(self, participants_list):
        self.participants = json.dumps(participants_list)

class Message(Base):
    tablename = 'messages'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    
    chat = relationship("Chat", back_populates="messages")
    user = relationship("User", back_populates="messages")

# ---------------------- МЕНЕДЖЕР ----------------------
class ChatManager:
    def __init__(self, database_url='sqlite:///Databases/Main.db'):
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    # ---------------------- Пользователи ----------------------
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
            user = User(email=email, name=name, phone=phone, about=about, photo=photo, blocked=blocked)
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

    def get_user_by_email(self, email):
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            return self._user_to_dict(user) or {}
        finally:
            session.close()
    def update_user(self, email, **kwargs):
            session = self.Session()
            try:
                user = session.query(User).filter(User.email == email).first()
                if not user:
                    return {"error": "Пользователь не найден"}
                allowed_fields = ['name', 'phone', 'about', 'photo', 'blocked', 'devices', 'chats']
                for field, value in kwargs.items():
                    if field in allowed_fields:
                        if field in ['devices', 'chats']:
                            getattr(user, f"set_{field}")(value)
                        else:
                            setattr(user, field, value)
                session.commit()
                return self._user_to_dict(user)
            except Exception as e:
                session.rollback()
                return {"error": str(e)}
            finally:
                session.close()

    def delete_user(self, email):
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return {"error": "Пользователь не найден"}
            user_data = self._user_to_dict(user)
            session.delete(user)
            session.commit()
            return {"success": True, "deleted_user": user_data}
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()

    def block_user(self, email, hours=24):
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return {"error": "Пользователь не найден"}
            user.blocked = datetime.utcnow() + timedelta(hours=hours)
            session.commit()
            return {"success": True, "blocked_until": user.blocked}
        finally:
            session.close()

    def is_user_blocked(self, email):
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

    def add_device(self, email, device_name, device_data):
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return {"error": "Пользователь не найден"}
            devices = user.get_devices()
            devices[device_name] = device_data
            user.set_devices(devices)
            session.commit()
            return {"success": True, "devices": devices}
        finally:
            session.close()

    # ---------------------- Чаты ----------------------
    def add_chat(self, name, participants=None, about=None, photo=None):
        session = self.Session()
        try:
            chat = Chat(name=name, about=about, photo=photo)
            if participants:
                chat.set_participants(participants)
            session.add(chat)
            session.commit()
            return {"success": True, "chat_id": chat.id}
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
# ---------------------- Сообщения ----------------------
    def add_message(self, chat_id, user_id, content):
        session = self.Session()
        try:
            msg = Message(chat_id=chat_id, user_id=user_id, content=content)
            session.add(msg)
            session.commit()
            return {"success": True, "message_id": msg.id}
        finally:
            session.close()

    def get_last_messages(self, chat_id, limit=50):
        session = self.Session()
        try:
            msgs = session.query(Message).filter(Message.chat_id == chat_id)\
                .order_by(Message.created.desc()).limit(limit).all()
            return [
                {
                    "id": m.id,
                    "chat_id": m.chat_id,
                    "user_id": m.user_id,
                    "user_name": m.user.name,
                    "content": m.content,
                    "created": m.created
                } for m in msgs
            ]
        finally:
            session.close