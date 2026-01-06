from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, select
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine, func, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.inspection import inspect
from datetime import datetime, timedelta

Base = declarative_base()

chat_participants = Table(
    "chat_participants",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("chat_id", ForeignKey("chats.id"), primary_key=True),
    Column("last_read",Integer,default=0)
)

'''
class chat_participants:
    __tablename__="chat_participants"

    user_id = Column(ForeignKey("users.id"), primary_key=True),
    chat_id = Column(ForeignKey("chats.id"), primary_key=True),
    last_read = Column(Integer,default=0)
'''

class Inventives(Base):
    __tablename__ = "inventives"

    id = Column(Integer,primary_key=True)
    emailrecive = Column(Integer, ForeignKey("users.email"), nullable=False)
    emailsent = Column(String)
    typeinventive = Column(String)
    message = Column(String,default=None)
    time = Column(DateTime, default=datetime.now())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    about = Column(Text)
    photo = Column(String(255))
    blocked = Column(DateTime)

    chats = relationship("Chat", secondary=chat_participants, back_populates="users")
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String(100))
    platform = Column(String(50))
    publickey = Column(String)
    publickeycrypt = Column(String)
    last_seen = Column(DateTime, default=datetime.now())
    created = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="devices")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(32), nullable=False)
    publickeycrypt = Column(String)
    about = Column(Text)
    photo = Column(String(255))
    created = Column(DateTime, default=datetime.now())

    users = relationship("User", secondary=chat_participants, back_populates="chats")
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    internal_id = Column(Integer, nullable=False)
    datatype = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.now())

    chat = relationship("Chat", back_populates="messages")
    user = relationship("User", back_populates="messages")

class DataBaseManager:

    def __init__(self, database_url="sqlite:///Databases/Main.db"):
        """
            created table in database_url as 
                - chat_participants  [
                    * user_id
                    * chat_id
                    * last_read_message
                ]
                - users  [
                    * id
                    * email
                    * name
                    * phone
                    * photo
                    * about
                    * blocked - none / datatime
                ]
                - chats  [
                    * id
                    * type - tehnic / p2p / group
                    * publickeycrypt
                    * name
                    * photo
                    * about
                    * created - datatime
                ]
                - messages  [
                    * id - global
                    * internal_id - local message id chat
                    * chat_id  
                    * user_id
                    * datatype -   txt /img /voice /file /folder
                    * content
                    * created
                ]
                - devices [
                    * id
                    * user_id
                    * name
                    * platform
                    * publickey
                    * publickeycrypt
                    * last_seen
                    * created
                ]
                -inventives[
                    * id
                    * emailsent
                    * emailrecive
                    * inventivetype
                    * message
                    * time
                ]
        """
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _get_info(self, users):
        result = []
        for u in users:
                devices = [
                    {"id": d.id, "name": d.name, "platform": d.platform, "last_seen": d.last_seen, "publickey": d.publickey, "publickeycrypt": d.publickeycrypt}
                    for d in u.devices
                ]
        result.append({
                    "id": u.id,
                    "email": u.email,
                    "name": u.name,
                    "phone": u.phone,
                    "about": u.about,
                    "photo": u.photo,
                    "blocked": u.blocked,
                    "devices": devices
                })
        return result

    def _to_dict(self,obj):
        if obj is None:
            return None
        try:
            return {
                key: (
                    value.isoformat() 
                    if hasattr(value, 'isoformat') 
                    else str(value) if hasattr(value, '__str__') and not isinstance(value, (int, float, bool, str))
                    else value
                )
                for key, value in obj.__dict__.items()
                if not key.startswith('_')
            }
        except:return None

    def _delete_obj(self,obj,id):
        session = self.Session()
        try:
            chat = session.get(obj,id)
            if not chat:
                return {"success":False,"error": f"id не найден"}
            session.delete(chat)
            session.commit()
            return {
                "success": True
            }
        except Exception as e:
            session.rollback()
            return {"success":False,"error": str(e)}
        finally:
            session.close()

    def add_user(self, email, name, phone=None, about=None, photo=None):
        session = self.Session()
        try:
            if session.query(User).filter_by(email=email).first():
                return {"success":False,"error": "user already exists"}

            user = User(
                email=email,
                name=name,
                phone=phone,
                about=about,
                photo=photo
            )

            session.add(user)
            session.commit()

            return {"success": True, "user_id": user.id, "email": user.email, "name": user.name}
        finally:
            session.close()

    def add_chat(self, name, user_ids, type="tehnic", about=None, photo=None, publickeycrypt=None):
        session = self.Session()
        try:
            user_ids = set(user_ids)

            users = (
                session.query(User)
                .filter(User.id.in_(user_ids))
                .all()
            )

            if not users:
                return {"success":False,"error": "no valid users"}

            chat = Chat(name=name, about=about, photo=photo, type=type, publickeycrypt=publickeycrypt)
            chat.users.extend(users)

            session.add(chat)
            session.commit()

            return {
                "success": True,
                "chat_id": chat.id,
                "added_users": [u.id for u in users]
            }
        except Exception as e:
            session.rollback()
            return {"success":False,
                    "error": str(e)}
        finally:
            session.close()

    def add_message(self, chat_id, user_id, datatype, content, tmc=None):
        session = self.Session()
        try:
            last_id = session.query(
                func.max(Message.internal_id)
            ).filter_by(chat_id=chat_id).scalar() or 0
            if tmc is None:
                tmc = datetime.now()
            msg = Message(
                chat_id=chat_id,
                user_id=user_id,
                internal_id=last_id + 1,
                datatype=datatype,
                content=content,
                created = tmc
            )

            session.add(msg)
            session.commit()
            return {"success": True, "message_id": msg.id, "internal_id": msg.internal_id, "time": tmc}
        finally:
            session.close()

    def read_message(self,user_id,chat_id,internal_id):
        session = self.Session()
        try:
            session.execute(
                update(chat_participants)
                .where(
                    chat_participants.c.user_id == user_id,
                    chat_participants.c.chat_id == chat_id,
                    chat_participants.c.last_read < internal_id
                )
                .values(last_read=internal_id)
            )
            session.commit()
            return {"success": True}
        finally:
            session.close()

    def add_device(self, user_id, name, publickey, publickeycrypt, platform=None):
        session = self.Session()
        try:
            device = Device(
                user_id=user_id,
                name=name,
                platform=platform,
                publickey=publickey,
                publickeycrypt=publickeycrypt,
                last_seen=datetime.now(),
                created=datetime.now()
            )
            session.add(device)
            session.commit()
            return {"success": True, "device_id": device.id}
        finally:
            session.close()

    def add_Inventive(self,emailrecive,emailsent,inventivetype,message=None):
        session = self.Session()
        try:
            inventive = Inventives(
                emailrecive=emailrecive,
                emailsent=emailsent,
                typeinventive=inventivetype,
                message=message,
                time=datetime.now(),
            )
            session.add(inventive)
            session.commit()
            return {"success": True, "inventive_id": inventive.id}
        finally:
            session.close()

    def get_user_chats(self, user_id):
        session = self.Session()
        try:
            user = session.get(User, user_id)
            if not user:
                return []
            return [self._to_dict(chat) for chat in user.chats]
        finally:
            session.close()

    def get_user_devices(self, user_id):
        session = self.Session()
        try:
            devices = session.query(Device).filter_by(user_id=user_id).all()
            return [
                {"id": d.id, "name": d.name, "platform": d.platform, "last_seen": d.last_seen}
                for d in devices
            ]
        finally:
            session.close()

    def get_user_Inventives(self, user_email):
        session = self.Session()
        try:
            inventives = session.query(Inventives).filter_by(emailrecive=user_email).all()
            return [
                {"id": d.id, "emailsent": d.emailsent, "message": d.message, "typeinventive": d.typeinventive, "time":d.time}
                for d in inventives
            ]
        finally:
            session.close()

    def get_user_by_email(self, email):
        session = self.Session()
        try:
            user = session.query(User).filter_by(email=email).first()
            if not user:
                return None
            return self._get_info([user])[0]
        finally:
            session.close()

    def get_user_by_id(self, id):
        session = self.Session()
        try:
            user = session.get(User, id)
            if not user:
                return None
            return self._get_info([user])[0]
        finally:
            session.close()

    def get_ChatParticipants(self,chat_id):
            session = self.Session() 
            participants = session.query(chat_participants).filter_by(chat_id=chat_id).all()
            return [{"id":p[0]} for p in participants]

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
                User.id.ilike(f'%{name_pattern}%')
            ).all()
            if users is None:return []
            if len(users)<1:
                return []
            return self._get_info(users)
            
        finally:
            session.close()

    def delete_User(self, user_id=None,user_email=None):
        if user_email is not None:
            id=self.get_user_by_email(user_email)["user_id"]
            return self._delete_obj(User, id)
        if user_id is not None:
            return self._delete_obj(User, user_id)
        return None
    
    def delete_Chat(self, chat_id):
        return self._delete_obj(Chat, chat_id)
    
    def delete_Device(self, device_id):
        return self._delete_obj(Device, device_id)
    
    def delete_message(self, message_id):
        return self._delete_obj(Message, message_id)
    
    def delete_Inventive(self, Inventive_id):
        return self._delete_obj(Inventives, Inventive_id)
    
    def update_user(self, email, **kwargs):
        """['name', 'phone', 'about', 'photo', 'blocked']"""
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return {"success":False,"error": f"Пользователь с email {email} не найден"}
            allowed_fields = ['name', 'phone', 'about', 'photo', 'blocked']
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, str(value))
            session.commit()
            return self._user_to_dict(user)
        except Exception as e:
            session.rollback()
            return {"success":False,"error": str(e)}
        finally:
            session.close()

    def update_chat(self, id, **kwargs):
        """['name', 'participants', 'about', 'photo']"""
        session = self.Session()
        try:
            chat = session.query(Chat).filter(Chat.id == id).first()
            if not chat:
                return {"success":False,"error":"id не найден"}
            allowed_fields = ['name', 'participants', 'about', 'photo']
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(chat, field):
                    setattr(chat, field, str(value))
            session.commit()
            return {"success": True}
        except Exception as e:
            session.rollback()
            return {"success":False,
                "error": str(e)}
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
                return {"success":False,"error": "Сообщение не найдено"}

            msg.content = new_content
            msg.datatype = datatype
            session.commit()

            return {
                "success": True,
            }
        except Exception as e:
            session.rollback()
            return {
                "success":False,
                "error": str(e)}
        finally:
            session.close()
    def update_device(self, id, **kwargs):
        """[publickey publickeycrypt lastseen]"""
        session = self.Session()
        try:
            device = session.query(Device).filter(Device.id == id).first()
            if not device:
                return {"success":False,"error":"id не найден"}
            allowed_fields = ['publickey', 'publickeycrypt', 'lastseen']
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(device, field):
                    setattr(device, field, str(value))
            session.commit()
            return {"success": True}
        except Exception as e:
            session.rollback()
            return {"success":False,
                "error": str(e)}
        finally:
            session.close()     

    def is_user_blocked(self, email):
        """Проверить заблокирован ли пользователь"""
        session = self.Session()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user or not user.blocked:
                return False
            if user.blocked < datetime.now():
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
                return {"success":False,"error": "Пользователь не найден"}
            user.blocked = datetime.now() + timedelta(hours=hours)
            session.commit()
            
            return {
                "success": True,
                "message": f"Пользователь заблокирован до {user.blocked}",
                "blocked_until": user.blocked
            }
        except Exception as e:
            session.rollback()
            return {"success":False,"error": str(e)}
        finally:
            session.close()

    def get_messages_before(self, chat_id, before_id=None, limit=30):
        session = self.Session()
        try:
            q = session.query(Message).filter(Message.chat_id == chat_id)
            if before_id:
                q = q.filter(Message.internal_id < before_id)

            messages = (
                q.order_by(Message.internal_id.desc())
                .limit(limit)
                .all()
            )

            return [self._to_dict(msg)  for msg in messages if msg is not None]
        finally:
            session.close()

    def get_unread_messages(self, user_id, chat_id):
        session = self.Session()
        try:
            last_read = session.execute(
                select(chat_participants.c.last_read)
                .where(
                    (chat_participants.c.user_id == user_id) &
                    (chat_participants.c.chat_id == chat_id)
                )
            ).scalar() or 0

            messages = (
                session.query(Message)
                .filter(
                    Message.chat_id == chat_id,
                    Message.internal_id > last_read
                )
                .order_by(Message.internal_id)
                .all()
            )
            return [self._to_dict(msg)  for msg in messages if msg is not None]
        finally:
            session.close()

    def getALL_unread_messages(self, user_id):
        session = self.Session()
        try:
            last_read = session.execute(
                select(chat_participants.c.last_read)
                .where(
                    (chat_participants.c.user_id == user_id)
                )
            ).scalar() or 0

            messages = (
                session.query(Message)
                .filter(
                    Message.internal_id > last_read
                )
                .order_by(Message.internal_id)
                .all()
            )
            return [self._to_dict(msg)  for msg in messages if msg is not None]
        finally:
            session.close()
