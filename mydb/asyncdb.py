from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, select, func, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.inspection import inspect
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json

Base = declarative_base()

chat_participants = Table(
    "chat_participants",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("chat_id", ForeignKey("chats.id"), primary_key=True),
    Column("last_read", Integer, default=0)
)

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
    last_seen = Column(DateTime, default=datetime.now)
    created = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="devices")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    about = Column(Text)
    photo = Column(String(255))
    created = Column(DateTime, default=datetime.now)

    users = relationship("User", secondary=chat_participants, back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    internal_id = Column(Integer, nullable=False)
    datatype = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.now)

    chat = relationship("Chat", back_populates="messages")
    user = relationship("User", back_populates="messages")


class AsyncDataBaseManager:
    def __init__(self, database_url: str = "sqlite+aiosqlite:///Databases/Main.db"):
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, 
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Явное создание таблиц"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы")
    
    def _get_info(self, users: List[User]) -> List[Dict]:
        """Преобразование списка пользователей в словари"""
        result = []
        for u in users:
            devices = [
                {
                    "id": d.id,
                    "name": d.name,
                    "platform": d.platform,
                    "last_seen": d.last_seen,
                    "publickey": d.publickey,
                    "publickeycrypt": d.publickeycrypt
                }
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

    def _to_dict(self, obj: Any) -> Optional[Dict]:
        """Преобразование объекта SQLAlchemy в словарь"""
        if obj is None:
            return None
        try:
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):
                    if hasattr(value, 'isoformat'):
                        result[key] = value.isoformat()
                    elif hasattr(value, '__str__') and not isinstance(value, (int, float, bool, str)):
                        result[key] = str(value)
                    else:
                        result[key] = value
            return result
        except Exception:
            return None

    # ===================== ОСНОВНЫЕ МЕТОДЫ =====================
    
    async def add_user(self, email: str, name: str, phone: str = None, 
                      about: str = None, photo: str = None) -> Dict:
        """Добавление пользователя"""
        async with self.async_session() as session:
            # Проверяем существование пользователя
            result = await session.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                return {"success": False, "error": "user already exists"}

            # Создаем пользователя
            user = User(
                email=email,
                name=name,
                phone=phone,
                about=about,
                photo=photo
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            return {
                "success": True,
                "user_id": user.id,
                "email": user.email,
                "name": user.name
            }

    async def add_chat(self, name: str, user_ids: List[int], 
                      about: str = None, photo: str = None) -> Dict:
        """Добавление чата"""
        async with self.async_session() as session:
            user_ids = set(user_ids)

            # Получаем пользователей
            result = await session.execute(
                select(User).where(User.id.in_(user_ids))
            )
            users = result.scalars().all()

            if not users:
                return {"success": False, "error": "no valid users"}

            # Создаем чат
            chat = Chat(name=name, about=about, photo=photo)
            chat.users.extend(users)

            session.add(chat)
            await session.commit()
            await session.refresh(chat)

            return {
                "success": True,
                "chat_id": chat.id,
                "added_users": [u.id for u in users]
            }

    async def add_message(self, chat_id: int, user_id: int, 
                         datatype: str, content: str) -> Dict:
        """Добавление сообщения"""
        async with self.async_session() as session:
            # Получаем последний internal_id
            result = await session.execute(
                select(func.max(Message.internal_id))
                .where(Message.chat_id == chat_id)
            )
            last_id = result.scalar() or 0

            # Создаем сообщение
            msg = Message(
                chat_id=chat_id,
                user_id=user_id,
                internal_id=last_id + 1,
                datatype=datatype,
                content=content,
                created=datetime.now()
            )

            session.add(msg)
            await session.commit()
            await session.refresh(msg)
            
            return {
                "success": True,
                "message_id": msg.id,
                "internal_id": msg.internal_id
            }

    async def read_message(self, user_id: int, chat_id: int, internal_id: int) -> Dict:
        """Отметка сообщения как прочитанного"""
        async with self.async_session() as session:
            await session.execute(
                update(chat_participants)
                .where(
                    chat_participants.c.user_id == user_id,
                    chat_participants.c.chat_id == chat_id,
                    chat_participants.c.last_read < internal_id
                )
                .values(last_read=internal_id)
            )
            await session.commit()
            return {"success": True}

    async def add_device(self, user_id: int, name: str, publickey: str, 
                        publickeycrypt: str, platform: str = None) -> Dict:
        """Добавление устройства"""
        async with self.async_session() as session:
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
            await session.commit()
            await session.refresh(device)
            
            return {"success": True, "device_id": device.id}

    # ===================== ПОЛУЧЕНИЕ ДАННЫХ =====================
    
    async def get_user_chats(self, user_id: int) -> List[Dict]:
        """Получение чатов пользователя"""
        async with self.async_session() as session:
            user = await session.get(User, user_id)
            if not user:
                return []
            
            return [self._to_dict(chat) for chat in user.chats]

    async def get_user_devices(self, user_id: int) -> List[Dict]:
        """Получение устройств пользователя"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Device).where(Device.user_id == user_id)
            )
            devices = result.scalars().all()
            
            return [
                {
                    "id": d.id,
                    "name": d.name,
                    "platform": d.platform,
                    "last_seen": d.last_seen
                }
                for d in devices
            ]

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Получение пользователя по email"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            return self._get_info([user])[0]

    async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Получение пользователя по ID"""
        async with self.async_session() as session:
            user = await session.get(User, user_id)
            if not user:
                return None
            
            return self._get_info([user])[0]

    async def search_users_by(self, pattern: str, by: str = "name") -> List[Dict]:
        """Поиск пользователей"""
        async with self.async_session() as session:
            stmt = select(User)
            
            match by:
                case "name":
                    stmt = stmt.where(User.name.ilike(f'%{pattern}%'))
                case "email":
                    stmt = stmt.where(User.email.ilike(f'%{pattern}%'))
                case "phone":
                    stmt = stmt.where(User.phone.ilike(f'%{pattern}%'))
                case "id":
                    stmt = stmt.where(User.id.ilike(f'%{pattern}%'))
                case _:
                    return []
            
            result = await session.execute(stmt)
            users = result.scalars().all()
            
            if not users:
                return []
            
            return self._get_info(users)

    # ===================== УДАЛЕНИЕ =====================
    
    async def _delete_obj(self, obj_class, obj_id: int) -> Dict:
        """Удаление объекта"""
        async with self.async_session() as session:
            try:
                obj = await session.get(obj_class, obj_id)
                if not obj:
                    return {"success": False, "error": f"id не найден"}
                
                await session.delete(obj)
                await session.commit()
                return {"success": True}
            except Exception as e:
                await session.rollback()
                return {"success": False, "error": str(e)}

    async def delete_user(self, user_id: int = None, user_email: str = None) -> Dict:
        """Удаление пользователя"""
        if user_email:
            user_info = await self.get_user_by_email(user_email)
            if not user_info:
                return {"success": False, "error": "Пользователь не найден"}
            user_id = user_info["id"]
        
        if user_id:
            return await self._delete_obj(User, user_id)
        
        return {"success": False, "error": "Не указан user_id или email"}

    async def delete_chat(self, chat_id: int) -> Dict:
        """Удаление чата"""
        return await self._delete_obj(Chat, chat_id)

    async def delete_device(self, device_id: int) -> Dict:
        """Удаление устройства"""
        return await self._delete_obj(Device, device_id)

    async def delete_message(self, message_id: int) -> Dict:
        """Удаление сообщения"""
        return await self._delete_obj(Message, message_id)

    # ===================== ОБНОВЛЕНИЕ =====================
    
    async def update_user(self, email: str, **kwargs) -> Dict:
        """Обновление пользователя"""
        async with self.async_session() as session:
            try:
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    return {"success": False, "error": f"Пользователь с email {email} не найден"}
                
                allowed_fields = ['name', 'phone', 'about', 'photo', 'blocked']
                for field, value in kwargs.items():
                    if field in allowed_fields and hasattr(user, field):
                        setattr(user, field, value)
                
                await session.commit()
                return self._to_dict(user)
            except Exception as e:
                await session.rollback()
                return {"success": False, "error": str(e)}

    async def update_chat(self, chat_id: int, **kwargs) -> Dict:
        """Обновление чата"""
        async with self.async_session() as session:
            try:
                chat = await session.get(Chat, chat_id)
                if not chat:
                    return {"success": False, "error": "id не найден"}
                
                allowed_fields = ['name', 'about', 'photo']
                for field, value in kwargs.items():
                    if field in allowed_fields and hasattr(chat, field):
                        setattr(chat, field, value)
                
                await session.commit()
                return {"success": True}
            except Exception as e:
                await session.rollback()
                return {"success": False, "error": str(e)}

    async def update_message(self, chat_id: int, chat_message_id: int, 
                           new_content: str, datatype: str) -> Dict:
        """Обновление сообщения"""
        async with self.async_session() as session:
            try:
                result = await session.execute(
                    select(Message)
                    .where(
                        Message.chat_id == chat_id,
                        Message.internal_id == chat_message_id
                    )
                )
                msg = result.scalar_one_or_none()

                if not msg:
                    return {"success": False, "error": "Сообщение не найдено"}

                msg.content = new_content
                msg.datatype = datatype
                await session.commit()

                return {"success": True}
            except Exception as e:
                await session.rollback()
                return {"success": False, "error": str(e)}

    async def update_device(self, device_id: int, **kwargs) -> Dict:
        """Обновление устройства"""
        async with self.async_session() as session:
            try:
                device = await session.get(Device, device_id)
                if not device:
                    return {"success": False, "error": "id не найден"}
                
                allowed_fields = ['publickey', 'publickeycrypt', 'last_seen', 'name', 'platform']
                for field, value in kwargs.items():
                    if field in allowed_fields and hasattr(device, field):
                        if field == 'last_seen' and isinstance(value, str):
                            # Преобразуем строку в datetime если нужно
                            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        setattr(device, field, value)
                
                await session.commit()
                return {"success": True}
            except Exception as e:
                await session.rollback()
                return {"success": False, "error": str(e)}

    # ===================== БЛОКИРОВКИ =====================
    
    async def is_user_blocked(self, email: str) -> bool:
        """Проверка блокировки пользователя"""
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.blocked:
                return False
            
            if user.blocked < datetime.now():
                user.blocked = None
                await session.commit()
                return False
            
            return True

    async def block_user(self, email: str, hours: int = 24) -> Dict:
        """Блокировка пользователя"""
        async with self.async_session() as session:
            try:
                result = await session.execute(
                    select(User).where(User.email == email)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    return {"success": False, "error": "Пользователь не найден"}
                
                user.blocked = datetime.now() + timedelta(hours=hours)
                await session.commit()
                
                return {
                    "success": True,
                    "message": f"Пользователь заблокирован до {user.blocked}",
                    "blocked_until": user.blocked
                }
            except Exception as e:
                await session.rollback()
                return {"success": False, "error": str(e)}

    # ===================== СООБЩЕНИЯ =====================
    
    async def get_messages_before(self, chat_id: int, before_id: int = None, 
                                 limit: int = 30) -> List[Dict]:
        """Получение сообщений до определенного ID"""
        async with self.async_session() as session:
            stmt = select(Message).where(Message.chat_id == chat_id)
            
            if before_id:
                stmt = stmt.where(Message.internal_id < before_id)
            
            stmt = stmt.order_by(Message.internal_id.desc()).limit(limit)
            
            result = await session.execute(stmt)
            messages = result.scalars().all()
            
            return [self._to_dict(msg) for msg in messages if msg]

    async def get_unread_messages(self, user_id: int, chat_id: int) -> List[Dict]:
        """Получение непрочитанных сообщений"""
        async with self.async_session() as session:
            # Получаем last_read
            result = await session.execute(
                select(chat_participants.c.last_read)
                .where(
                    (chat_participants.c.user_id == user_id) &
                    (chat_participants.c.chat_id == chat_id)
                )
            )
            last_read = result.scalar() or 0

            # Получаем непрочитанные сообщения
            result = await session.execute(
                select(Message)
                .where(
                    Message.chat_id == chat_id,
                    Message.internal_id > last_read
                )
                .order_by(Message.internal_id)
            )
            messages = result.scalars().all()
            
            return [self._to_dict(msg) for msg in messages if msg]

    async def get_all_users(self) -> Dict:
        """Получение всех пользователей (новый метод)"""
        async with self.async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            return {
                "success": True,
                "users": self._get_info(users) if users else []
            }

    async def get_chat_info(self, chat_id: int) -> Dict:
        """Получение информации о чате"""
        async with self.async_session() as session:
            chat = await session.get(Chat, chat_id)
            if not chat:
                return {"success": False, "error": "Chat not found"}
            
            return {
                "success": True,
                "chat": self._to_dict(chat),
                "participants_count": len(chat.users),
                "messages_count": len(chat.messages)
            }