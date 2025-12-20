from sqlalchemy import create_engine, Column, String, Boolean, Text, CheckConstraint, Integer,DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
from datetime import datetime, timedelta

engine = create_engine('sqlite:///Main.db')
Base = declarative_base()

class Chat(Base):
    __tablename__ = 'Chats'

    chatid = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    participants = Column(Text)
    about = Column(Text(1024))
    photo = Column(String(255))
    created = Column(DateTime, default=None)
    message = relationship("Message", back_populates="chat")

class User(Base):
    __tablename__ = 'Users'
    
    email = Column(String(255), primary_key=True)
    userid = Column(Integer, nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20))
    about = Column(Text(1024))
    photo = Column(String(255))
    blocked = Column(DateTime, default=None)
    devices = Column(Text)
    chats = Column(Text)
    message = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = 'Messages'

    messageid = Column(Integer, primary_key=True)
    type = Column(String(100), nullable=False)
    participants = Column(Text)