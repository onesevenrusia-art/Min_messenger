from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

# --- Пользователи ---
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    about = Column(Text)
    photo = Column(String(255))
    blocked = Column(DateTime, default=None)
    
    messages = relationship("Message", back_populates="user")  # связь с сообщениями

# --- Чаты ---
class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    participants = Column(Text)  # можно хранить список email в JSON
    about = Column(Text)
    photo = Column(String(255))
    created = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="chat")  # связь с сообщениями

# --- Сообщения ---
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    
    chat = relationship("Chat", back_populates="messages")
    user = relationship("User", back_populates="messages")

# --- Создание БД ---
engine = create_engine('sqlite:///Databases/Main.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()